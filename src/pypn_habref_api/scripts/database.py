import configparser
import io
import os
import subprocess
from urllib.parse import urlparse
import zipfile


from pathlib import Path

import click
import requests
import sqlalchemy
import psycopg2


CURDIR = Path(os.path.dirname(os.path.abspath(__file__)))
DATADIR = CURDIR.parent / 'data'

habref_file = [
    'HABITATS.HABREF_NOTES_40.csv',  
    'HABREF_DESCRIPTION_40.csv', 
    'HABREF_SOURCES_40.csv',
    'HABREF_VALIDITE_40.csv',
    'HABREF_40.csv',   
    'HABREF_DESCRIPTION_NOHTML_40.csv',  'HABREF_STATUTS_40.csv'   'TYPOREF_40.csv'
'HABREF_CORRESP_HAB_40.csv',     'HABREF_LIEN_SOURCES_40.csv',        'HABREF_TERR_40.csv',      'TYPOREF_FIELDS_40.csv',
'HABREF_CORRESP_TAXON_40.csv',   'HABREF_NOHTML_40.csv',             'HABREF_TYPE_REL_40.csv',  'TYPOREF_NOHTML_40.csv'
]


def download_habref():
    if not os.path.isdir('/tmp/habref'):
        os.mkdir('/tmp/habref')
    os.chdir('/tmp/habref')
    if not os.path.isfile('habref.zip'):
        print('DOWNLOADING HABREF...')
        resp = requests.get(
            'https://geonature.fr/data/inpn/habitats/HABREF_40.zip'
        )
        if resp.status_code != 200:
            raise Exception("Erreur while downlading Habref")
        open('habref.zip', 'wb').write(resp.content)
        z = zipfile.ZipFile('habref.zip')
        z.extractall()
        print('DONE')
    else:
        'Habref is already downloaded... keep going'


def check_if_schema_exist(database_uri):
    engine = database_connect(database_uri)
    with engine.connect():
        sql = '''
        SELECT count(*) FROM information_schema.schemata WHERE schema_name = 'ref_habitat';
        '''
        r = engine.execute(sql).fetchone()
        if r[0] == 1:
            raise Exception('Schema ref_habitat already exist')
        click.echo("Schema ref_habitat does not exist, let's install it !")


def database_connect(database_uri):
    '''
    return an database sqlalchemy engine
    '''
    return sqlalchemy.create_engine(database_uri)

def run_sql_scripts(engine, databse_uri):
    uri = urlparse(databse_uri)
    db_name = uri.path[1:]
    conn = engine.connect()
    sql_schema = str(DATADIR / 'habref.sql')
    conn.execute(open(sql_schema).read())
    conn.execute('COMMIT')
    # execute in bash because we need to be superuser to execute it
    command = "sudo -u postgres -s psql -d {db_name}  -f {file}".format(
        db_name=db_name,
        file=str(DATADIR / 'data_inpn_habref.sql')
    )
    code = subprocess.call(command.split())
    if code != 0:
        raise Exception(
            'An error occured while insering Habref data in ref_habitat schema'
        )
    conn.execute('COMMIT')
    conn.close()



@click.group()
def main():
    pass

@main.command()
@click.argument('db_uri')
def install_schema(db_uri):
    click.echo('Initialized the schema ref_habitat in, {}'.format(db_uri))
    check_if_schema_exist(db_uri)
    download_habref()
    engine = database_connect(db_uri)
    run_sql_scripts(engine, db_uri)
    click.echo('\n\n ')
    click.echo('\o/ ')
    click.echo('## Install sucessfully schema ref_habitat  ##')


@main.command()
@click.argument('db_uri')
def drop_schema(db_uri):
    click.echo('Drop the schema in, {}'.format(db_uri))

if __name__ == '__main__':
    main()