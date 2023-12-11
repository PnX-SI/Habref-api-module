import pytest

from pypn_habref_api.models import BibListHabitat, Habref
from pypn_habref_api.env import db
from .conftest import app


@pytest.fixture(scope="session")
def bib_list(app):
    new_list = BibListHabitat(list_name="list test")
    habitat = db.session.execute(db.select(Habref).limit(1)).scalar_one()
    new_list.habitats.append(habitat)
    db.session.add(new_list)
    return new_list
