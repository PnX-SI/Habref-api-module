"""insert inpn data in ref_habitats schema

Revision ID: 46e91e738845
Create Date: 2021-09-23 10:38:23.132666

"""

from zipfile import ZipFile
from collections import OrderedDict

from alembic import op
import sqlalchemy as sa

from utils_flask_sqla.migrations.utils import logger, open_remote_file


# revision identifiers, used by Alembic.
revision = "46e91e738845"
down_revision = None
branch_labels = ("habitats_inpn_data",)
depends_on = ("62e63cd6135d",)  # ref_habitats schema


base_url = "https://geonature.fr/data/inpn/habitats/"
table_files = OrderedDict(
    [
        ("bib_habref_typo_rel", "HABREF_TYPE_REL_50.csv"),
        ("bib_habref_statuts", "HABREF_STATUTS_50.csv"),
        ("habref_sources", "HABREF_SOURCES_50.csv"),
        ("typoref", "TYPOREF_50.csv"),
        ("habref", "HABREF_NOHTML_50.csv"),
        ("habref_corresp_hab", "HABREF_CORRESP_HAB_50.csv"),
        ("habref_corresp_taxon", "HABREF_CORRESP_TAXON_50.csv"),
        ("cor_habref_terr_statut", "HABREF_TERR_50.csv"),
        ("typoref_fields", "TYPOREF_FIELDS_50.csv"),
        ("cor_habref_description", "HABREF_DESCRIPTION_NOHTML_50.csv"),
        ("cor_hab_source", "HABREF_LIEN_SOURCES_50.csv"),
    ]
)


def upgrade():
    cursor = op.get_bind().connection.cursor()
    with open_remote_file(base_url, "HABREF_50.zip", open_fct=ZipFile) as archive:
        for table, filename in table_files.items():
            with archive.open(filename) as f:
                logger.info(f"Insert INPN data in {table}…")
                cursor.copy_expert(
                    f"""
                COPY ref_habitats.{table} FROM STDIN WITH CSV HEADER DELIMITER E';'
                """,
                    f,
                )

    logger.info("Populate table autocomplete_habitat…")
    op.execute(
        """
    INSERT INTO ref_habitats.autocomplete_habitat
    SELECT
    cd_hab,
    h.cd_typo,
    lb_code,
    lb_nom_typo,
    concat(lb_code, ' - ', lb_hab_fr, ' ', lb_hab_fr_complet)
    FROM ref_habitats.habref h
    JOIN ref_habitats.typoref t ON t.cd_typo = h.cd_typo
    """
    )


def downgrade():
    # FIXME is this ok to truncate all tables?
    for table in ["autocomplete_habitat"] + list(table_files.keys())[::-1]:
        op.execute(f"TRUNCATE TABLE ref_habitats.{table} CASCADE")
