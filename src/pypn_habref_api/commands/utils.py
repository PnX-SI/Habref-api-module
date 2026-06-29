import csv
import os
from csv import DictReader
from io import TextIOWrapper

import sqlalchemy as sa
from sqlalchemy import inspect as sa_inspect, text
from sqlalchemy.schema import (
    Table,
    MetaData,
    PrimaryKeyConstraint,
    ForeignKeyConstraint,
)

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

    testTable = Table(final_table_name, MetaData(), schema=schema, autoload_with=db.session.connection())

    for col in testTable.columns:
        if col.name in table_fields:
            table_fields[col.name] = f"{table_fields[col.name]}::{col.type}"
    table_fields_list = list(table_fields.values())

    db.session.execute(
        f"""
    INSERT INTO {schema}.{final_table_name} ({", ".join(table_fields_key_list)})
        SELECT {", ".join(table_fields_list)}
        FROM {schema}.{table_name};
    """
    )
    table.drop(bind=db.session.connection())


def empty_table(table_name, db, schema=""):
    inspector = sa_inspect(db.engine)

    # Récupère les foreign keys
    foreign_keys = inspector.get_foreign_keys(table_name, schema=schema)
    db.session.execute("SET session_replication_role = 'replica'")
    for fk in foreign_keys:
        constraint_name = fk["name"]
        if constraint_name:  # Vérifie que le nom existe
            db.session.execute(
                f"ALTER TABLE {schema}.{table_name} DROP CONSTRAINT {constraint_name} CASCADE"
            )
    db.session.execute(f"DELETE FROM {schema}.{table_name}")
    return foreign_keys


def restore_constraints(table_name, db, constraints, schema=""):
    if constraints is None:
        return
    for constraint in constraints:
        if isinstance(constraint, PrimaryKeyConstraint):
            cols = ", ".join(str(col).split(".")[1] for col in constraint.columns)
            db.session.execute(
                f"ALTER TABLE {schema}.{table_name} ADD CONSTRAINT {constraint.name} UNIQUE ({cols})"
            )
        elif isinstance(constraint, ForeignKeyConstraint):
            cols = ", ".join(str(col).split(".")[1] for col in constraint.columns)
            ref_cols = ", ".join(
                str(col).split(".")[1] for col in constraint.references[0].columns
            )
            db.session.execute(
                f"ALTER TABLE {schema}.{table_name} ADD CONSTRAINT {constraint.name} FOREIGN KEY {cols} REFERENCES {constraint.references[0].table.name}({ref_cols})"
            )


def get_referencing_tables(table_name, db, schema="", exclude_tables=None):
    """Trouve toutes les tables qui ont des FK pointant vers table_name,
    en excluant les tables listées dans exclude_tables."""
    exclude_tables = set(exclude_tables or [])
    inspector = sa_inspect(db.engine)
    referencing_tables = []

    for other_schema in inspector.get_schema_names():
        if other_schema in ("pg_catalog", "information_schema", "pg_toast"):
            continue
        try:
            for other_table in inspector.get_table_names(schema=other_schema):
                if other_schema == schema and other_table in exclude_tables:
                    continue
                for fk in inspector.get_foreign_keys(other_table, schema=other_schema):
                    referred_schema = fk.get("referred_schema") or other_schema
                    if fk["referred_table"] == table_name and (
                        not schema or referred_schema == schema
                    ):
                        referencing_tables.append(
                            {
                                "schema": other_schema,
                                "table": other_table,
                                "fk_column": fk["constrained_columns"][0],
                                "ref_column": fk["referred_columns"][0],
                            }
                        )
        except Exception as e:
            print(f"Impossible d'inspecter le schéma {other_schema}: {e}")

    return referencing_tables


def export_orphans_to_csv(ref_table, new_ref_table, pk_col, output_path, db, schema="", exclude_tables=None):
    """
    Compare ref_table (ancienne version) et new_ref_table (nouvelle version importée)
    et exporte dans un CSV unique toutes les valeurs de pk_col présentes dans les tables
    référençantes qui n'existent plus dans new_ref_table.

    Colonnes CSV : table_name, schema, fk_column, fk_value, nb_lignes_affectees
    """
    ref_full = f"{schema}.{new_ref_table}" if schema else new_ref_table
    referencing = get_referencing_tables(ref_table, db, schema=schema, exclude_tables=exclude_tables)

    rows = []
    for ref in referencing:
        src_full = f"{ref['schema']}.{ref['table']}"
        fk_col = ref["fk_column"]
        result = db.session.execute(
            text(
                f"""
                SELECT t.{fk_col}, COUNT(*) AS nb_lignes
                FROM {src_full} t
                WHERE t.{fk_col} IS NOT NULL
                  AND NOT EXISTS (
                      SELECT 1 FROM {ref_full} r WHERE r.{pk_col} = t.{fk_col}
                  )
                GROUP BY t.{fk_col}
                ORDER BY t.{fk_col}
                """
            )
        ).fetchall()

        for fk_value, nb_lignes in result:
            rows.append(
                {
                    "table_name": ref["table"],
                    "schema": ref["schema"],
                    "fk_column": fk_col,
                    "fk_value": fk_value,
                    "nb_lignes_affectees": nb_lignes,
                }
            )

    if not rows:
        return 0

    dirname = os.path.dirname(output_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["table_name", "schema", "fk_column", "fk_value", "nb_lignes_affectees"],
        )
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)
