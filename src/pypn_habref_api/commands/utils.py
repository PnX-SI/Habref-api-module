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
