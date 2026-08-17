# coding: utf8
from typing import Optional

from sqlalchemy import Boolean, Column, ForeignKey, Integer, Table, Unicode
from sqlalchemy.orm import Mapped, mapped_column
from utils_flask_sqla.serializers import serializable

from pypn_habref_api.env import db as DB


@serializable
class BibHabrefTypoRel(DB.Model):
    __tablename__ = "bib_habref_typo_rel"
    __table_args__ = {"schema": "ref_habitats"}
    cd_type_rel: Mapped[int] = mapped_column(Integer, primary_key=True)
    lb_type_rel: Mapped[Optional[str]] = mapped_column(Unicode)
    lb_rel: Mapped[Optional[str]] = mapped_column(Unicode)
    corresp_hab: Mapped[Optional[bool]] = mapped_column(Boolean)
    corresp_esp: Mapped[Optional[bool]] = mapped_column(Boolean)
    corresp_syn: Mapped[Optional[bool]] = mapped_column(Boolean)


@serializable
class CorespHab(DB.Model):
    __tablename__ = "habref_corresp_hab"
    __table_args__ = {"schema": "ref_habitats"}
    cd_corresp_hab: Mapped[int] = mapped_column(Integer, primary_key=True)
    cd_hab_entre: Mapped[int] = mapped_column(Integer, ForeignKey("ref_habitats.habref.cd_hab"))
    cd_hab_sortie: Mapped[Optional[int]] = mapped_column(Integer)
    cd_type_relation: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("ref_habitats.bib_habref_typo_rel.cd_type_rel")
    )
    lb_condition: Mapped[Optional[str]] = mapped_column(Unicode)
    lb_remarques: Mapped[Optional[str]] = mapped_column(Unicode)
    validite: Mapped[Optional[bool]] = mapped_column(Boolean)
    cd_typo_entre: Mapped[Optional[int]] = mapped_column(Integer)
    cd_typo_sortie: Mapped[Optional[int]] = mapped_column(Integer)
    date_crea: Mapped[Optional[int]] = mapped_column(Integer)
    diffusion: Mapped[Optional[bool]] = mapped_column(Boolean)

    type_rel = DB.relationship("BibHabrefTypoRel", lazy="select")


@serializable
class TypoRef(DB.Model):
    __tablename__ = "typoref"
    __table_args__ = {"schema": "ref_habitats"}
    cd_typo: Mapped[int] = mapped_column(Integer, primary_key=True)
    cd_table: Mapped[Optional[str]] = mapped_column(Unicode)
    lb_nom_typo: Mapped[Optional[str]] = mapped_column(Unicode)
    nom_jeu_donnees: Mapped[Optional[str]] = mapped_column(Unicode)
    date_creation: Mapped[Optional[str]] = mapped_column(Unicode)
    date_mise_jour_table: Mapped[Optional[str]] = mapped_column(Unicode)
    date_mise_jour_metadonnees: Mapped[Optional[str]] = mapped_column(Unicode)
    auteur_typo: Mapped[Optional[str]] = mapped_column(Unicode)
    auteur_table: Mapped[Optional[str]] = mapped_column(Unicode)
    territoire: Mapped[Optional[str]] = mapped_column(Unicode)
    organisme: Mapped[Optional[str]] = mapped_column(Unicode)
    langue: Mapped[Optional[str]] = mapped_column(Unicode)
    presentation: Mapped[Optional[str]] = mapped_column(Unicode)
    description: Mapped[Optional[str]] = mapped_column(Unicode)
    origine: Mapped[Optional[str]] = mapped_column(Unicode)
    ref_biblio: Mapped[Optional[str]] = mapped_column(Unicode)
    mots_cles: Mapped[Optional[str]] = mapped_column(Unicode)
    referencement: Mapped[Optional[str]] = mapped_column(Unicode)
    diffusion: Mapped[Optional[str]] = mapped_column(Unicode)
    derniere_modif: Mapped[Optional[str]] = mapped_column(Unicode)
    type_table: Mapped[Optional[str]] = mapped_column(Unicode)
    cd_typo_entre: Mapped[Optional[int]] = mapped_column(Integer)
    cd_typo_sortie: Mapped[Optional[int]] = mapped_column(Integer)
    niveau_inpn: Mapped[Optional[int]] = mapped_column(Integer)

    habitats = DB.relationship("Habref", back_populates="typo")


cor_list_habitat = Table(
    "cor_list_habitat",
    DB.metadata,
    Column("id_cor_list", Integer, primary_key=True),
    Column("id_list", Integer, ForeignKey("ref_habitats.bib_list_habitat.id_list")),
    Column("cd_hab", Integer, ForeignKey("ref_habitats.habref.cd_hab")),
    schema="ref_habitats",
)


@serializable
class Habref(DB.Model):
    __tablename__ = "habref"
    __table_args__ = {"schema": "ref_habitats"}
    cd_hab: Mapped[int] = mapped_column(Integer, primary_key=True)
    fg_validite: Mapped[str] = mapped_column(Unicode)
    cd_typo: Mapped[int] = mapped_column(Integer, ForeignKey("ref_habitats.typoref.cd_typo"))
    lb_code: Mapped[Optional[str]] = mapped_column(Unicode)
    lb_hab_fr: Mapped[Optional[str]] = mapped_column(Unicode)
    lb_hab_fr_complet: Mapped[Optional[str]] = mapped_column(Unicode)
    lb_hab_en: Mapped[Optional[str]] = mapped_column(Unicode)
    lb_auteur: Mapped[Optional[str]] = mapped_column(Unicode)
    niveau: Mapped[Optional[int]] = mapped_column(Integer)
    lb_niveau: Mapped[Optional[str]] = mapped_column(Unicode)
    cd_hab_sup: Mapped[Optional[int]] = mapped_column(Integer)
    path_cd_hab: Mapped[Optional[str]] = mapped_column(Unicode)
    france: Mapped[Optional[str]] = mapped_column(Unicode)
    lb_description: Mapped[Optional[str]] = mapped_column(Unicode)

    typo = DB.relationship("TypoRef", lazy="joined", back_populates="habitats")
    correspondances = DB.relationship("CorespHab", lazy="select")
    lists = DB.relationship(
        "BibListHabitat", secondary=cor_list_habitat, back_populates="habitats"
    )


@serializable
class BibListHabitat(DB.Model):
    __tablename__ = "bib_list_habitat"
    __table_args__ = {"schema": "ref_habitats"}
    id_list: Mapped[int] = mapped_column(Integer, primary_key=True)
    list_name: Mapped[str] = mapped_column(Unicode)
    habitats = DB.relationship("Habref", secondary=cor_list_habitat, back_populates="lists")


@serializable
class AutoCompleteHabitat(DB.Model):
    __tablename__ = "autocomplete_habitat"
    __table_args__ = {"schema": "ref_habitats"}
    cd_hab: Mapped[int] = mapped_column(Integer, primary_key=True)
    cd_typo: Mapped[int] = mapped_column(Integer)
    lb_code: Mapped[Optional[str]] = mapped_column(Unicode)
    lb_nom_typo: Mapped[str] = mapped_column(Unicode)
    search_name: Mapped[str] = mapped_column(Unicode)
    lists = DB.relationship(
        BibListHabitat,
        primaryjoin=(cor_list_habitat.c.cd_hab == cd_hab),
        secondary=cor_list_habitat,
        viewonly=True,
    )
