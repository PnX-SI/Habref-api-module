from importlib import import_module


from flask import jsonify, Blueprint, request, current_app
from sqlalchemy import desc, func, select
from sqlalchemy.orm.exc import NoResultFound

from utils_flask_sqla.response import json_resp

from pypn_habref_api.models import (
    Habref,
    AutoCompleteHabitat,
    TypoRef,
    CorespHab,
    BibHabrefTypoRel,
    BibListHabitat,
)
from pypn_habref_api.env import db as DB


routes = Blueprint("habref", __name__)


@routes.route("/search/<field>/<ilike>", methods=["GET"])
@json_resp
def getSearchInField(field, ilike):
    """
    Get the first 20 result of Habref table for a given field with an ilike query
    Use trigram algo to add relevance

    .. :quickref: Habref;

    :params field: a Habref column
    :type field: str
    :param ilike: the ilike where expression to filter
    :type ilike:str

    :returns: Array of dict
    """
    habref_columns = Habref.__table__.columns
    if field in habref_columns:
        value = unquote(ilike)
        value = value.replace(" ", "%")
        column = habref_columns[field]
        q = (
            select(Habref, func.similarity(column, value).label("idx_trgm"))
            .filter(column.ilike("%" + value + "%"))
            .order_by(desc("idx_trgm"))
        )

        data = DB.session.scalars(q.limit(20)).all()
        return [d[0].as_dict() for d in data]
    else:
        "No column found in Taxref for {}".format(field), 500


@routes.route("/habitat/<int:cd_hab>", methods=["GET"])
@json_resp
def get_hab(cd_hab):
    """
    Get one habitat with its correspondances

    .. :quickref: Habref;

    :params cd_hab: a cd_hab
    :type cd_hab: int
    """
    one_hab = DB.session.get(Habref, cd_hab).as_dict(True)
    if "correspondances" in one_hab:
        for cor in one_hab["correspondances"]:
            hab_sortie = DB.session.get(Habref, cor["cd_hab_sortie"]).as_dict(True)
            cor["habref"] = hab_sortie
    return one_hab


@routes.route("/habitats/autocomplete", methods=["GET"])
@json_resp
def get_habref_autocomplete():
    """
    Get all habref items of a list for autocomplete

    .. :quickref: Habref;

    :query id_list int: the id of the habref list
    :query search_name str: the pattern to filter with
    :query cd_typo int: filter by typology
    :query limit int: number of results, default = 20

    :returns: Array<AutoCompleteHabitat>
    """
    params = request.args
    search_name = params.get("search_name")
    q = select(
        AutoCompleteHabitat,
        func.similarity(AutoCompleteHabitat.search_name, search_name).label("idx_trgm"),
    )

    if "id_list" in params:
        q = q.where(AutoCompleteHabitat.lists.any(id_list=params["id_list"]))

    if "search_name" in params:
        search_name = search_name.replace(" ", "%")
        q = q.where(AutoCompleteHabitat.search_name.ilike("%" + search_name + "%"))

    # filter by typology
    if "cd_typo" in params:
        q = q.where(AutoCompleteHabitat.cd_typo == params.get("cd_typo"))

    limit = request.args.get("limit", 20)
    # order by lb_code to have first high hierarchy hab first
    q = q.order_by(AutoCompleteHabitat.lb_code.asc())
    # order by trigram
    q = q.order_by(desc("idx_trgm"))
    data = DB.session.scalars(q.limit(limit)).all()
    if data:
        return [d.as_dict() for d in data]
    else:
        return []


@routes.route("/typo", methods=["GET"])
@json_resp
def get_typo():
    """
    Get all typology

    .. :quickref: Habref;

    :query int id_list: return only the typology of a given id_list
    :returns: Array<TypoRef>
    """
    params = request.args

    q = select(TypoRef)

    id_list = params.get("id_list", type=int)
    if id_list:
        q = q.where(TypoRef.habitats.any(Habref.lists.any(BibListHabitat.id_list == id_list)))
    data = DB.session.scalars(q.order_by(TypoRef.lb_nom_typo)).all()

    return [d.as_dict() for d in data]


@routes.route("/correspondance/<int:cd_hab>", methods=["GET"])
@json_resp
def get_coresp(cd_hab):
    """
    Get all correspondances in other typo from a cd_hab

    .. :quickref: Habref;

    :params cd_hab: a cd_hab
    :type cd_hab: int
    """
    q = (
        select(CorespHab, BibHabrefTypoRel, Habref, TypoRef)
        .join(BibHabrefTypoRel, CorespHab.cd_type_relation == BibHabrefTypoRel.cd_type_rel)
        .join(Habref, Habref.cd_hab == CorespHab.cd_hab_sortie)
        .join(TypoRef, TypoRef.cd_typo == Habref.cd_typo)
        .where(CorespHab.cd_hab_entre == cd_hab)
    )

    data = []
    for d in DB.session.scalars(q).unique().all():
        temp = {**d[0].as_dict(), **d[1].as_dict(), **d[2].as_dict(), **d[3].as_dict()}
        data.append(temp)

    return data
