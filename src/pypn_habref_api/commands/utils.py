from csv import DictReader
from io import TextIOWrapper
from zipfile import ZipFile

import sqlalchemy as sa
from sqlalchemy import inspect as sa_inspect, text as sa_text
from sqlalchemy.schema import (
    Table,
    MetaData,
    PrimaryKeyConstraint,
    ForeignKeyConstraint,
)

from utils_flask_sqla.migrations.utils import open_remote_file

from pypn_habref_api.env import db


def get_csv_field_names(f, encoding, delimiter):
    if encoding == "WIN1252":  # postgresql encoding
        encoding = "cp1252"  # python encoding
    t = TextIOWrapper(f, encoding=encoding)
    reader = DictReader(t, delimiter=delimiter)
    field_names = reader.fieldnames
    t.detach()  # avoid f to be closed on t garbage collection
    f.seek(0)
    return field_names


"""
Insert CSV file into specified table.
If source columns are specified, CSV file in copied in a temporary table,
then data restricted to specified source columns are copied in final table.
"""


def copy_from_csv(
    f,
    table_name,
    table_fields,
    schema="",
    header=True,
    encoding=None,
    delimiter=None,
    db=None,
):
    bind = db.session.get_bind()
    metadata = MetaData(bind=bind)
    engine = db.engine

    table_fields_list = list(table_fields.values())
    table_fields_key_list = list(table_fields.keys())

    final_table_name = table_name
    table_name = f"import_{table_name}"
    field_names = get_csv_field_names(f, encoding=encoding, delimiter=delimiter)
    field_names = list(map(lambda field_name: field_name.replace("\ufeff", ""), field_names))
    table = Table(
        table_name,
        metadata,
        *[sa.Column(c, sa.String) for c in map(str.lower, field_names)],
        schema=schema,
    )
    table.create(bind=db.session.connection())

    options = ["FORMAT CSV"]
    if header:
        options.append("HEADER")
    if encoding:
        options.append(f"ENCODING '{encoding}'")
    if delimiter:
        options.append(f"DELIMITER E'{delimiter}'")
    options = ", ".join(options)
    cursor = db.session.connection().connection.cursor()
    cursor.copy_expert(
        f"""
        COPY {schema}.{table_name}
        FROM STDIN WITH ({options})
    """,
        f,
    )

    testTable = Table(
        final_table_name, MetaData(), schema=schema, autoload_with=db.session.connection()
    )

    for col in testTable.columns:
        if col.name in table_fields:
            table_fields[col.name] = f"{table_fields[col.name]}::{col.type}"
    table_fields_list = list(table_fields.values())

    db.session.execute(f"""
    INSERT INTO {schema}.{final_table_name} ({", ".join(table_fields_key_list)})
        SELECT {", ".join(table_fields_list)}
        FROM {schema}.{table_name};
    """)
    table.drop(bind=db.session.connection())


def import_habref(logger, table_files, schema, base_url, num_version, archive_name):
    with open_remote_file(base_url, archive_name, open_fct=ZipFile) as archive:
        for table, value in table_files.items():
            logger.info(f"Insert HABREF v{num_version} {table}…")
            with archive.open(value["filename"]) as f:
                db.session.execute(sa_text(f"DROP TABLE IF EXISTS {schema}.tmp_{table}"))
                db.session.execute(
                    sa_text(f"CREATE TABLE {schema}.tmp_{table} AS TABLE {schema}.{table} WITH NO DATA")
                )
                copy_from_csv(
                    f,
                    f"tmp_{table}",
                    value["table_fields"],
                    encoding="UTF-8",
                    delimiter=";",
                    schema=schema,
                    db=db,
                )


def apply_habref(logger, table_files, schema):
    db.session.execute(sa_text("SET session_replication_role = 'replica'"))

    for table in reversed(list(table_files.keys())):
        logger.info(f"Vidage de {table}…")
        db.session.execute(sa_text(f"DELETE FROM {schema}.{table}"))

    for table in table_files.keys():
        logger.info(f"Remplissage de {table} depuis tmp_{table}…")
        db.session.execute(
            sa_text(f"INSERT INTO {schema}.{table} SELECT * FROM {schema}.tmp_{table}")
        )

    logger.info("Remplissage de autocomplete_habitat…")
    db.session.execute(sa_text(f"DELETE FROM {schema}.autocomplete_habitat"))
    db.session.execute(sa_text(f"""
        INSERT INTO {schema}.autocomplete_habitat
        SELECT
            cd_hab,
            h.cd_typo,
            lb_code,
            lb_nom_typo,
            concat(lb_code, ' - ', lb_hab_fr, ' ', lb_hab_fr_complet)
        FROM {schema}.habref h
        JOIN {schema}.typoref t ON t.cd_typo = h.cd_typo
    """))

    db.session.execute(sa_text("SET session_replication_role = 'origin'"))

    for table in reversed(list(table_files.keys())):
        logger.info(f"Suppression de tmp_{table}…")
        db.session.execute(sa_text(f"DROP TABLE IF EXISTS {schema}.tmp_{table}"))
