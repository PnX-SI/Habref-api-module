"""Create ref_habitats schema

Revision ID: 7d4235aa8483
Revises: 
Create Date: 2020-12-28 13:03:51.529053

"""
from alembic import op, context
import sqlalchemy as sa
import pkg_resources
from distutils.util import strtobool
from urllib.request import urlopen
import logging
from tempfile import TemporaryDirectory
from shutil import copyfileobj
from zipfile import ZipFile
from contextlib import ExitStack
import os, os.path


# revision identifiers, used by Alembic.
revision = '7d4235aa8483'
down_revision = None
branch_labels = ('habref',)
depends_on = None

schema = 'ref_habitats'
habref_url = 'https://geonature.fr/data/inpn/habitats/HABREF_50.zip'


logger = logging.getLogger('alembic.runtime.migration')


def upgrade():
    logger.info(f"Creating {schema} schema…")
    operations = pkg_resources.resource_string("pypn_habref_api.migrations", "data/habref.sql").decode('utf-8')
    op.execute(operations)
    if strtobool(context.get_x_argument(as_dictionary=True).get('habref-data', "true")):
        operations = pkg_resources.resource_string("pypn_habref_api.migrations", "data/data_inpn_habref.sql").decode('utf-8')
        habref_dir = context.get_x_argument(as_dictionary=True).get('habref-data-directory')
        with ExitStack() as stack:
            if not habref_dir:
                habref_dir = stack.enter_context(TemporaryDirectory())
            if not os.path.exists(habref_dir):
                os.mkdir(habref_dir)
            if not os.path.isfile(f"{habref_dir}/HABREF_TYPE_REL_50.csv")
                if not os.path.isfile(f"{habref_dir}/habref.zip")
                    logger.info("Downloading habref data…")
                    with urlopen(habref_url) as response, open(f'{habref_dir}/habref.zip', 'wb') as zip_file:
                        copyfileobj(response, zip_file)
                logger.info("Extracting habref data…")
                with ZipFile(f"{habref_dir}/habref.zip") as z:
                    z.extractall(path=habref_dir)
            cursor = op.get_bind().connection.cursor()
            for table, csvfile in [
                        ('bib_habref_typo_rel', 'HABREF_TYPE_REL_50.csv'),
                        ('bib_habref_statuts', 'HABREF_STATUTS_50.csv'),
                        ('habref_sources', 'HABREF_SOURCES_50.csv'),
                        ('typoref', 'TYPOREF_50.csv'),
                        ('habref', 'HABREF_NOHTML_50.csv'),
                        ('habref_corresp_hab', 'HABREF_CORRESP_HAB_50.csv'),
                        ('habref_corresp_taxon', 'HABREF_CORRESP_TAXON_50.csv'),
                        ('cor_habref_terr_statut', 'HABREF_TERR_50.csv'),
                        ('typoref_fields', 'TYPOREF_FIELDS_50.csv'),
                        ('cor_habref_description', 'HABREF_DESCRIPTION_NOHTML_50.csv'),
                        ('cor_hab_source', 'HABREF_LIEN_SOURCES_50.csv'),
                    ]:
                logger.info(f"Populating table {table}…")
                with open(f'{habref_dir}/{csvfile}') as f:
                    cursor.copy_expert(f"COPY {schema}.{table} FROM STDIN WITH CSV HEADER DELIMITER E';' ENCODING 'UTF-8'", file=f)
        operations = pkg_resources.resource_string("pypn_habref_api.migrations", "data/data_inpn_habref_post.sql").decode('utf-8')
        op.execute(operations)


def downgrade():
    op.execute('DROP SCHEMA ref_habitats CASCADE')
