import csv
import io
import logging
import os
import tempfile
import zipfile
from contextlib import contextmanager
from unittest.mock import patch

import pytest
from sqlalchemy import inspect as sa_inspect, text

from pypn_habref_api.commands.habref_v7 import apply_habref, import_habref, table_files
from pypn_habref_api.commands.utils import collect_orphan_rows, export_orphans_to_csv
from pypn_habref_api.env import db


def make_habref_zip():
    """ZIP minimal en mémoire — uniquement les en-têtes CSV, aucune ligne de données."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for config in table_files.values():
            csv_content = io.StringIO()
            writer = csv.writer(csv_content, delimiter=";")
            writer.writerow(config["table_fields"].values())
            zf.writestr(config["filename"], csv_content.getvalue().encode("utf-8"))
    buf.seek(0)
    return buf


@contextmanager
def tmp_tables():
    """Crée les tables tmp_* en copiant la structure des tables habref, et les supprime à la fin."""
    try:
        for table in table_files:
            db.session.execute(text(f"DROP TABLE IF EXISTS ref_habitats.tmp_{table}"))
            db.session.execute(
                text(
                    f"CREATE TABLE ref_habitats.tmp_{table} "
                    f"AS TABLE ref_habitats.{table} WITH NO DATA"
                )
            )
        db.session.flush()
        yield
    finally:
        for table in reversed(list(table_files.keys())):
            db.session.execute(text(f"DROP TABLE IF EXISTS ref_habitats.tmp_{table}"))
        db.session.flush()


@pytest.mark.usefixtures("app")
class TestImportHabref:
    def test_tmp_tables_created(self):
        """import_habref crée une table tmp_* pour chaque table de table_files."""
        logger = logging.getLogger()
        zip_data = make_habref_zip()

        @contextmanager
        def fake_open_remote(url, filename, open_fct=None):
            zip_data.seek(0)
            with zipfile.ZipFile(zip_data) as zf:
                yield zf

        try:
            with patch("pypn_habref_api.commands.habref_v7.open_remote_file", fake_open_remote):
                import_habref(logger, num_version="07", habref_archive_name="HABREF_70.zip")

            inspector = sa_inspect(db.engine)
            existing = inspector.get_table_names(schema="ref_habitats")
            for table in table_files:
                assert f"tmp_{table}" in existing
        finally:
            for table in reversed(list(table_files.keys())):
                db.session.execute(text(f"DROP TABLE IF EXISTS ref_habitats.tmp_{table}"))
            db.session.flush()


@pytest.mark.usefixtures("app")
class TestExportOrphans:
    def test_orphan_detected_in_csv(self):
        """Un cd_hab présent dans cor_list_habitat mais absent de tmp_habref apparaît dans le CSV."""
        orphan_cd_hab = db.session.execute(
            text("SELECT cd_hab FROM ref_habitats.habref LIMIT 1")
        ).scalar()

        with tmp_tables():
            db.session.execute(
                text(
                    "INSERT INTO ref_habitats.tmp_habref "
                    "SELECT * FROM ref_habitats.habref WHERE cd_hab != :cd"
                ),
                {"cd": orphan_cd_hab},
            )

            db.session.execute(text("SET session_replication_role = 'replica'"))
            db.session.execute(
                text(
                    "INSERT INTO ref_habitats.cor_list_habitat (id_cor_list, cd_hab) "
                    "SELECT COALESCE(MAX(id_cor_list), 0) + 1, :cd "
                    "FROM ref_habitats.cor_list_habitat"
                ),
                {"cd": orphan_cd_hab},
            )
            db.session.execute(text("SET session_replication_role = 'origin'"))
            db.session.flush()

            with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
                output_path = f.name
            try:
                orphan_rows = collect_orphan_rows(
                    ref_table="habref",
                    new_ref_table="tmp_habref",
                    pk_col="cd_hab",
                    db=db,
                    schema="ref_habitats",
                    exclude_tables=list(table_files.keys()),
                )
                nb = export_orphans_to_csv(orphan_rows, output_path)
                assert nb > 0
                with open(output_path) as f:
                    rows = list(csv.DictReader(f))
                assert any(int(r["fk_value"]) == orphan_cd_hab for r in rows)
            finally:
                os.unlink(output_path)
                db.session.execute(text("SET session_replication_role = 'replica'"))
                db.session.execute(
                    text("DELETE FROM ref_habitats.cor_list_habitat WHERE cd_hab = :cd"),
                    {"cd": orphan_cd_hab},
                )
                db.session.execute(text("SET session_replication_role = 'origin'"))
                db.session.flush()


@pytest.mark.usefixtures("app")
class TestApplyHabref:
    def test_tables_updated_and_tmp_dropped(self):
        """apply_habref remplace le contenu des tables réelles et supprime les tmp_*."""
        logger = logging.getLogger()

        count_before = db.session.execute(
            text("SELECT COUNT(*) FROM ref_habitats.habref")
        ).scalar()

        with tmp_tables():
            for table in table_files:
                db.session.execute(
                    text(
                        f"INSERT INTO ref_habitats.tmp_{table} "
                        f"SELECT * FROM ref_habitats.{table}"
                    )
                )
            db.session.flush()

            apply_habref(logger)
            db.session.flush()

            count_after = db.session.execute(
                text("SELECT COUNT(*) FROM ref_habitats.habref")
            ).scalar()
            assert count_after == count_before

            inspector = sa_inspect(db.engine)
            existing = inspector.get_table_names(schema="ref_habitats")
            for table in table_files:
                assert f"tmp_{table}" not in existing
