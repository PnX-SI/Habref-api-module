from zipfile import ZipFile
from collections import OrderedDict
import logging

from pypn_habref_api.models import BibListHabitat, Habref
from pypn_habref_api.env import db

from sqlalchemy.schema import Table, MetaData, PrimaryKeyConstraint

import click
from flask.cli import with_appcontext

from alembic import op

from utils_flask_sqla.migrations.utils import open_remote_file
from .utils import copy_from_csv, empty_table, restore_constraints

base_url = "https://geonature.fr/data/inpn/habitats/"
table_files = {
    "typoref": {
        "filename": "TYPOREF_70.csv",
        "table_fields": {
            "cd_typo": "CD_TYPO",
            "cd_table": "CD_TABLE",
            "lb_nom_typo": "LB_NOM_TYPO",
            "nom_jeu_donnees": "NOM_JEU_DONNEES",
            "date_creation": "DATE_CREATION",
            "auteur_typo": "AUTEUR_TYPO",
            "auteur_table": "AUTEUR_TABLE",
            "territoire": "TERRITOIRE",
            "organisme": "ORGANISME",
            "langue": "LANGUE",
            "presentation": "PRESENTATION",
            "description": "DESCRIPTION",
            "origine": "ORIGINE",
            "ref_biblio": "REF_BIBLIO",
            "mots_cles": "MOTS_CLES",
            "referencement": "REFERENCEMENT",
            "diffusion": "DIFFUSION",
            "derniere_modif": "DERNIERE_MODIF",
            "type_table": "TYPE_TABLE",
            "cd_typo_entre": "CD_TYPO_ENTRE",
            "cd_typo_sortie": "CD_TYPO_SORTIE",
        },
    },
    "bib_habref_typo_rel": {
        "filename": "HABREF_TYPE_REL_70.csv",
        "table_fields": {
            "cd_type_rel": "CD_TYPE_REL",
            "lb_type_rel": "LB_TYPE_REL",
            "lb_rel": "LB_REL",
            "corresp_hab": "CORRESP_HAB",
            "corresp_esp": "CORRESP_ESP",
            "corresp_syn": "CORRESP_SYN",
            "date_crea": "DATE_CREA",
            "date_modif": "DATE_MODIF",
        },
    },
    "bib_habref_statuts": {
        "filename": "HABREF_STATUTS.csv",
        "table_fields": {
            "statut": "STATUT",
            "description": "DESCRIPTION",
            "definition": "DEFINITION",
            "ordre": "ORDRE",
        },
    },
    "habref_sources": {
        "filename": "HABREF_SOURCES_70.csv",
        "table_fields": {
            "cd_source": "CD_SOURCE",
            "cd_doc": "CD_DOC",
            "type_source": "TYPE_SOURCE",
            "auteur_source": "AUTEUR_SOURCE",
            "date_source": "DATE_SOURCE",
            "lb_source": "LB_SOURCE",
            "lb_source_complet": "LB_SOURCE_COMPLET",
            "titre": "TITRE",
            "link": "LINK",
            "date_crea": "DATE_CREA",
            "date_modif": "DATE_MODIF",
        },
    },
    "habref": {
        "filename": "HABREF_70.csv",
        "table_fields": {
            "cd_hab": "CD_HAB",
            "fg_validite": "FG_VALIDITE",
            "cd_typo": "CD_TYPO",
            "lb_code": "LB_CODE",
            "lb_hab_fr": "LB_HAB_FR",
            "lb_hab_fr_complet": "LB_HAB_FR_COMPLET",
            "lb_hab_en": "LB_HAB_EN",
            "lb_auteur": "LB_AUTEUR",
            "niveau": "NIVEAU",
            "lb_niveau": "LB_NIVEAU",
            "cd_hab_sup": "CD_HAB_SUP",
            "path_cd_hab": "PATH_CD_HAB",
            "france": "FRANCE",
            "lb_description": "LB_DESCRIPTION",
        },
    },
    "habref_corresp_hab": {
        "filename": "HABREF_CORRESP_HAB_70.csv",
        "table_fields": {
            "cd_corresp_hab": "CD_CORRESP_HAB",
            "cd_hab_entre": "CD_HAB_ENTRE",
            "cd_hab_sortie": "CD_HAB_SORTIE",
            "cd_type_relation": "CD_TYPE_RELATION",
            "lb_condition": "LB_CONDITION",
            "lb_remarques": "LB_REMARQUES",
            "validite": "VALIDITE",
            "cd_typo_entre": "CD_TYPO_ENTRE",
            "cd_typo_sortie": "CD_TYPO_SORTIE",
        },
    },
    "habref_corresp_taxon": {
        "filename": "HABREF_CORRESP_TAXON_70.csv",
        "table_fields": {
            "cd_corresp_tax": "CD_CORRESP_TAX",
            "cd_hab_entre": "CD_HAB_ENTRE",
            "cd_nom": "CD_NOM",
            "cd_type_relation": "CD_TYPE_RELATION",
            "lb_condition": "LB_CONDITION",
            "lb_remarques": "LB_REMARQUES",
            "nom_cite": "NOM_CITE",
            "validite": "VALIDITE",
            "date_crea": "DATE_CREA",
            "date_modif": "DATE_MODIF",
        },
    },
    "cor_habref_terr_statut": {
        "filename": "HABREF_TERR_70.csv",
        "table_fields": {
            "cd_hab_ter": "CD_HAB_TERR",
            "cd_hab": "CD_HAB",
            "cd_sig_terr": "CD_SIG_TERR",
            "cd_statut_presence": "CD_STATUT_PRESENCE",
            "date_crea": "DATE_CREA",
            "date_modif": "DATE_MODIF",
        },
    },
    "typoref_fields": {
        "filename": "TYPOREF_FIELDS_70.csv",
        "table_fields": {
            "cd_hab_field": "CD_HAB_FIELD",
            "cd_typo": "CD_TYPO",
            "lb_hab_field": "LB_HAB_FIELD",
            "format_hab_field": "FORMAT_HAB_FIELD",
            "descript_hab_field": "DESCRIPT_HAB_FIELD",
            "ordre_hab_field": "ORDRE_HAB_FIELD",
            "length_hab_field": "LENGTH_HAB_FIELD",
            "lb_label": "LB_LABEL",
            "date_crea": "DATE_CREA",
            "date_modif": "DATE_MODIF",
        },
    },
    "cor_habref_description": {
        "filename": "HABREF_DESCRIPTION_70.csv",
        "table_fields": {
            "cd_hab_description": "CD_HAB_DESCRIPTION",
            "cd_hab": "CD_HAB",
            "cd_hab_field": "CD_HAB_FIELD",
            "cd_typo": "CD_TYPO",
            "lb_code": "LB_CODE",
            "lb_hab_field": "LB_HAB_FIELD",
            "valeurs": "VALEURS",
        },
    },
    "cor_hab_source": {
        "filename": "HABREF_LIEN_SOURCES_70.csv",
        "table_fields": {
            "cd_hab_lien_source": "CD_HAB_LIEN_SOURCE",
            "cd": "CD",
            "type_lien": "TYPE_LIEN",
            "cd_source": "CD_SOURCE",
            "origine": "ORIGINE",
            "date_crea": "DATE_CREA",
            "date_modif": "DATE_MODIF",
        },
    },
}


def import_habref(logger, num_version, habref_archive_name):
    with open_remote_file(base_url, habref_archive_name, open_fct=ZipFile) as archive:
        for table, value in table_files.items():
            logger.info(f"Insert HABREF v{num_version} {table}…")
            with archive.open(value["filename"]) as f:
                db.execute(
                    f"CREATE TABLE ref_habitats.tmp_{table} AS TABLE ref_habitats.{table} WITH NO DATA;"
                )
                copy_from_csv(
                    f,
                    f"tmp_{table}",
                    value["table_fields"],
                    encoding="UTF-8",
                    delimiter=";",
                    schema="ref_habitats",
                    db=db,
                )


@click.command()
@with_appcontext
def import_v07():
    logger = logging.getLogger()

    import_habref(
        logger,
        num_version="07",
        habref_archive_name="HABREF_70.zip",
    )

    logger.info("Committing…")
    db.session.commit()
