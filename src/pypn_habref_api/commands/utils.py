from csv import DictReader
from io import TextIOWrapper

import sqlalchemy as sa
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.schema import (
    Table,
    MetaData,
    PrimaryKeyConstraint,
    ForeignKeyConstraint,
)


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

    testTable = Table(final_table_name, db.metadata, schema=schema, autoload_with=engine)

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


def detect_changes():
    pass


def detect_missing_cd_hab():
    op.create_table(
        "tmp_missing_cd_hab",
        Column("cd_hab", Integer, primary_key=True),
        schema="ref_habitats",
    )
    pass


def test():
    inspector = sa_inspect(db.engine)

    # Trouve toutes les tables qui référencent cette table
    broken_refs = []

    foreign_keys = inspector.get_foreign_keys(table_name, schema=schema)

    # Désactive les contraintes FK
    db.session.execute(text("SET session_replication_role = 'replica'"))
    try:
        # Vide la table
        db.session.execute(text(f"TRUNCATE TABLE {table_full_name}"))
        db.session.commit()

        # Charge les nouvelles données si une fonction est fournie
        if data_loader_func:
            data_loader_func(db)

        # Réactive les contraintes
        db.session.execute(text("SET session_replication_role = 'origin'"))
        db.session.commit()

        # Vérifie les références cassées
        broken = check_broken_references(table_name, db, schema)
        if broken:
            print("⚠️ ATTENTION : Références cassées détectées !")
            for ref in broken:
                print(
                    f"  - Table {ref['table']}.{ref['column']} : {ref['broken_count']} lignes orphelines"
                )
            return False, broken

        print("✓ Aucune référence cassée détectée")
        return True, foreign_keys

    except Exception as e:
        db.session.rollback()
        db.session.execute(text("SET session_replication_role = 'origin'"))
        db.session.commit()
        raise e


def get_referencing_tables(table_name, db, schema=""):
    """Trouve toutes les tables (tous schémas) qui ont des FK pointant vers table_name"""
    inspector = sa_inspect(db.engine)
    referencing_tables = []

    all_schemas = inspector.get_schema_names()

    for other_schema in all_schemas:
        if other_schema in ("pg_catalog", "information_schema", "pg_toast"):
            continue

        try:
            for other_table in inspector.get_table_names(schema=other_schema):
                fks = inspector.get_foreign_keys(other_table, schema=other_schema)

                for fk in fks:
                    referred_schema = fk.get("referred_schema", other_schema)

                    if fk["referred_table"] == table_name and (
                        not schema or referred_schema == schema
                    ):
                        referencing_tables.append(
                            {
                                "schema": other_schema,
                                "table": other_table,
                                "constraint_name": fk["name"],
                                "fk_column": fk["constrained_columns"][0],
                                "ref_column": fk["referred_columns"][0],
                                "referred_schema": referred_schema,
                            }
                        )
        except Exception as e:
            print(f"Impossible d'inspecter le schéma {other_schema}: {e}")
            continue

    return referencing_tables


def check_broken_references():
    inspector = sa_inspect(db.engine)

    # Trouve toutes les tables qui référencent cette table
    broken_refs = []

    for other_table in inspector.get_table_names(schema=schema):
        fks = inspector.get_foreign_keys(other_table, schema=schema)

        for fk in fks:
            # Si cette FK pointe vers notre table
            if fk["referred_table"] == table_name:
                fk_column = fk["constrained_columns"][0]
                ref_column = fk["referred_columns"][0]

                table_full = f"{schema}.{other_table}" if schema else other_table
                ref_full = f"{schema}.{table_name}" if schema else table_name

                # Requête pour trouver les orphelins
                query = text(
                    f"""
                    SELECT COUNT(*) as broken_count
                    FROM {table_full} t
                    WHERE t.{fk_column} IS NOT NULL
                    AND NOT EXISTS (
                        SELECT 1 FROM {ref_full} r 
                        WHERE r.{ref_column} = t.{fk_column}
                    )
                """
                )

                result = db.session.execute(query).fetchone()
                if result[0] > 0:
                    broken_refs.append(
                        {"table": other_table, "column": fk_column, "broken_count": result[0]}
                    )

    return broken_refs
