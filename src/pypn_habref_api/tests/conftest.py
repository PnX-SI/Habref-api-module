import pytest

from pypn_habref_api import create_app
from pypn_habref_api.env import db


@pytest.fixture(scope='session')
def app():
    return create_app()


@pytest.fixture(scope='session')
def _session(app):
    return db.session
