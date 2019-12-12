
# coding: utf8
from __future__ import (unicode_literals, print_function,
                        absolute_import, division)
from importlib import import_module
from flask import current_app
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select, func
from utils_flask_sqla.serializers import serializable

# get or create the SQLAlchemy DB instance
DB = current_app.config.get('DB', import_module('.env', 'pypn_habref_api').DB)
@serializable
class BibHabrefTypoRel(db.Model):
    __tablename__ = "bib_habref_typo_rel"
    __table_args__ = {"schema": "ref_habitat"}
    cd_type_rel = db.Column(db.Integer, primary_key=True)
    lb_type_rel = db.Column(db.Unicode)
    lb_rel = db.Column(db.Unicode)
    corresp_hab = db.Column(db.Boolean)
    corresp_esp = db.Column(db.Boolean)
    corresp_syn = db.Column(db.Boolean)


@serializable
class CorespHab(db.Model):
    __tablename__ = "habref_corresp_hab"
    __table_args__ = {"schema": "ref_habitat"}
    cd_corresp_hab = db.Column(db.Integer, primary_key=True)
    cd_hab_entre = db.Column(
        db.Integer, ForeignKey("ref_habitat.habref.cd_hab"))
    cd_hab_sortie = db.Column(db.Integer)
    cd_type_relation = db.Column(
        db.Integer, ForeignKey("ref_habitat.bib_habref_typo_rel.cd_type_rel")
    )
    lb_condition = db.Column(db.Unicode)
    lb_remarques = db.Column(db.Unicode)
    validite = db.Column(db.Boolean)
    cd_typo_entre = db.Column(db.Integer)
    cd_typo_sortie = db.Column(db.Integer)
    date_crea = db.Column(db.Integer)
    diffusion = db.Column(db.Boolean)

    type_rel = db.relationship("BibHabrefTypoRel", lazy="select")


@serializable
class TypoRef(db.Model):
    __tablename__ = "typoref"
    __table_args__ = {"schema": "ref_habitat"}
    cd_typo = db.Column(db.Integer, primary_key=True)
    cd_table = db.Column(db.Unicode)
    lb_nom_typo = db.Column(db.Unicode)
    nom_jeu_donnees = db.Column(db.Unicode)
    date_creation = db.Column(db.Unicode)
    date_mise_jour_table = db.Column(db.Unicode)
    date_mise_jour_metadonnees = db.Column(db.Unicode)
    auteur_typo = db.Column(db.Unicode)
    auteur_table = db.Column(db.Unicode)
    territoire = db.Column(db.Unicode)
    organisme = db.Column(db.Unicode)
    langue = db.Column(db.Unicode)
    presentation = db.Column(db.Unicode)
    description = db.Column(db.Unicode)
    origine = db.Column(db.Unicode)
    ref_biblio = db.Column(db.Unicode)
    mots_cles = db.Column(db.Unicode)
    referencement = db.Column(db.Unicode)
    diffusion = db.Column(db.Unicode)
    derniere_modif = db.Column(db.Unicode)
    type_table = db.Column(db.Unicode)
    cd_typo_entre = db.Column(db.Integer)
    cd_typo_sortie = db.Column(db.Integer)
    niveau_inpn = db.Column(db.Integer)


@serializable
class Habref(db.Model):
    __tablename__ = "habref"
    __table_args__ = {"schema": "ref_habitat"}
    cd_hab = db.Column(db.Integer, primary_key=True)
    fg_validite = db.Column(db.Unicode)
    cd_typo = db.Column(db.Integer, ForeignKey("ref_habitat.typoref.cd_typo"))
    lb_code = db.Column(db.Unicode)
    lb_hab_fr = db.Column(db.Unicode)
    lb_hab_fr_complet = db.Column(db.Unicode)
    lb_hab_en = db.Column(db.Unicode)
    lb_auteur = db.Column(db.Unicode)
    niveau = db.Column(db.Integer)
    lb_niveau = db.Column(db.Unicode)
    cd_hab_sup = db.Column(db.Integer)
    path_cd_hab = db.Column(db.Unicode)
    france = db.Column(db.Unicode)
    lb_description = db.Column(db.Unicode)

    typo = db.relationship("TypoRef", lazy="select")
    correspondances = db.relationship("CorespHab", lazy="select")


@serializable
class BibListHabitat(db.Model):
    __tablename__ = "bib_list_habitat"
    __table_args__ = {"schema": "ref_habitat"}
    id_list = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.Unicode)


@serializable
class CorListHabitat(db.Model):
    __tablename__ = "cor_list_habitat"
    __table_args__ = {"schema": "ref_habitat"}
    id_cor_list = db.Column(db.Integer, primary_key=True)
    id_list = db.Column(db.Integer, ForeignKey(
        "ref_habitat.bib_list_habitat.id_list"))
    cd_hab = db.Column(db.Integer, ForeignKey("ref_habitat.habref.cd_hab"))


@serializable
class AutoCompleteHabitat(db.Model):
    __tablename__ = "autocomplete_habitat"
    __table_args__ = {"schema": "ref_habitat"}
    cd_hab = db.Column(db.Integer, primary_key=True)
    cd_typo = db.Column(db.Integer)
    lb_code = db.Column(db.Unicode)
    lb_nom_typo = db.Column(db.Unicode)
    search_name = db.Column(db.Unicode)
