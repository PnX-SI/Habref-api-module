# coding: utf8
from __future__ import unicode_literals, print_function, absolute_import, division
from importlib import import_module
from flask import current_app
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select, func
from utils_flask_sqla.serializers import serializable

# get or create the SQLAlchemy DB instance
DB = current_app.config.get("DB", import_module(".env", "pypn_habref_api").DB)


@serializable
class BibHabrefTypoRel(DB.Model):
    __tablename__ = "bib_habref_typo_rel"
    __table_args__ = {"schema": "ref_habitats"}
    cd_type_rel = DB.Column(DB.Integer, primary_key=True)
    lb_type_rel = DB.Column(DB.Unicode)
    lb_rel = DB.Column(DB.Unicode)
    corresp_hab = DB.Column(DB.Boolean)
    corresp_esp = DB.Column(DB.Boolean)
    corresp_syn = DB.Column(DB.Boolean)


@serializable
class CorespHab(DB.Model):
    __tablename__ = "habref_corresp_hab"
    __table_args__ = {"schema": "ref_habitats"}
    cd_corresp_hab = DB.Column(DB.Integer, primary_key=True)
    cd_hab_entre = DB.Column(
        DB.Integer, ForeignKey("ref_habitats.habref.cd_hab"))
    cd_hab_sortie = DB.Column(DB.Integer)
    cd_type_relation = DB.Column(
        DB.Integer, ForeignKey("ref_habitats.bib_habref_typo_rel.cd_type_rel")
    )
    lb_condition = DB.Column(DB.Unicode)
    lb_remarques = DB.Column(DB.Unicode)
    validite = DB.Column(DB.Boolean)
    cd_typo_entre = DB.Column(DB.Integer)
    cd_typo_sortie = DB.Column(DB.Integer)
    date_crea = DB.Column(DB.Integer)
    diffusion = DB.Column(DB.Boolean)

    type_rel = DB.relationship("BibHabrefTypoRel", lazy="select")


@serializable
class TypoRef(DB.Model):
    __tablename__ = "typoref"
    __table_args__ = {"schema": "ref_habitats"}
    cd_typo = DB.Column(DB.Integer, primary_key=True)
    cd_table = DB.Column(DB.Unicode)
    lb_nom_typo = DB.Column(DB.Unicode)
    nom_jeu_donnees = DB.Column(DB.Unicode)
    date_creation = DB.Column(DB.Unicode)
    date_mise_jour_table = DB.Column(DB.Unicode)
    date_mise_jour_metadonnees = DB.Column(DB.Unicode)
    auteur_typo = DB.Column(DB.Unicode)
    auteur_table = DB.Column(DB.Unicode)
    territoire = DB.Column(DB.Unicode)
    organisme = DB.Column(DB.Unicode)
    langue = DB.Column(DB.Unicode)
    presentation = DB.Column(DB.Unicode)
    description = DB.Column(DB.Unicode)
    origine = DB.Column(DB.Unicode)
    ref_biblio = DB.Column(DB.Unicode)
    mots_cles = DB.Column(DB.Unicode)
    referencement = DB.Column(DB.Unicode)
    diffusion = DB.Column(DB.Unicode)
    derniere_modif = DB.Column(DB.Unicode)
    type_table = DB.Column(DB.Unicode)
    cd_typo_entre = DB.Column(DB.Integer)
    cd_typo_sortie = DB.Column(DB.Integer)
    niveau_inpn = DB.Column(DB.Integer)


@serializable
class Habref(DB.Model):
    __tablename__ = "habref"
    __table_args__ = {"schema": "ref_habitats"}
    cd_hab = DB.Column(DB.Integer, primary_key=True)
    fg_validite = DB.Column(DB.Unicode)
    cd_typo = DB.Column(DB.Integer, ForeignKey("ref_habitats.typoref.cd_typo"))
    lb_code = DB.Column(DB.Unicode)
    lb_hab_fr = DB.Column(DB.Unicode)
    lb_hab_fr_complet = DB.Column(DB.Unicode)
    lb_hab_en = DB.Column(DB.Unicode)
    lb_auteur = DB.Column(DB.Unicode)
    niveau = DB.Column(DB.Integer)
    lb_niveau = DB.Column(DB.Unicode)
    cd_hab_sup = DB.Column(DB.Integer)
    path_cd_hab = DB.Column(DB.Unicode)
    france = DB.Column(DB.Unicode)
    lb_description = DB.Column(DB.Unicode)

    typo = DB.relationship("TypoRef", lazy="joined")
    correspondances = DB.relationship("CorespHab", lazy="select")


@serializable
class BibListHabitat(DB.Model):
    __tablename__ = "bib_list_habitat"
    __table_args__ = {"schema": "ref_habitats"}
    id_list = DB.Column(DB.Integer, primary_key=True)
    list_name = DB.Column(DB.Unicode)


@serializable
class CorListHabitat(DB.Model):
    __tablename__ = "cor_list_habitat"
    __table_args__ = {"schema": "ref_habitats"}
    id_cor_list = DB.Column(DB.Integer, primary_key=True)
    id_list = DB.Column(DB.Integer, ForeignKey(
        "ref_habitats.bib_list_habitat.id_list"))
    cd_hab = DB.Column(DB.Integer, ForeignKey("ref_habitats.habref.cd_hab"))


@serializable
class AutoCompleteHabitat(DB.Model):
    __tablename__ = "autocomplete_habitat"
    __table_args__ = {"schema": "ref_habitats"}
    cd_hab = DB.Column(DB.Integer, primary_key=True)
    cd_typo = DB.Column(DB.Integer)
    lb_code = DB.Column(DB.Unicode)
    lb_nom_typo = DB.Column(DB.Unicode)
    search_name = DB.Column(DB.Unicode)
