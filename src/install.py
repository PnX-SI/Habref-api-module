import configparser
import io
import os
import subprocess
import zipfile


from pathlib import Path

import requests
import psycopg2


CURDIR = Path(os.path.dirname(os.path.abspath(__file__)))
DATADIR = CURDIR.parent / 'data'


def download_habref():
    if not os.path.isdir('/tmp/habref'):
        os.mkdir('/tmp/habref')
        os.chdir('/tmp/habref')
        print('DOWNLOADING HABREF...')
        resp = requests.get(
            'https://geonature.fr/data/inpn/habitats/HABREF_40.zip')
        if resp.status_code != 200:
            raise Exception("Erreur while downlading Habref")
        z = zipfile.ZipFile(io.StringIO(resp.content))
        z.extractall()
        print('DONE')
    else:
        'Habref is already downloaded... keep going'


def parse_config(settings_file):
    virtual_config = io.StringIO()

    virtual_config.write('[config]\n')
    virtual_config.write(open(settings_file).read())
    virtual_config.seek(0, os.SEEK_SET)

    config = configparser.ConfigParser()
    config.readfp(virtual_config)
    return config['config']


def database_connect(config):
    return psycopg2.connect(
        host=config['db_host'],
        database=config['db_name'],
        user=config['user_pg'],
        password=config['user_pg_pass']
    )


def run_sql_scripts(conn, db_name):
    cur = conn.cursor()
    sql_schema = str(DATADIR / 'habref.sql')
    cur.execute(open(sql_schema).read())
    conn.commit()
    cur.close()
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


def run_install_db(settings_file):
    download_habref()
    config = parse_config(settings_file)
    connection = database_connect(config)
    run_sql_scripts(connection, config['db_name'])
    connection.close()
