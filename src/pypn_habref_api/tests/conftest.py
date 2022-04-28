import pytest

from pypn_habref_api import create_app
from pypn_habref_api.env import db


@pytest.fixture(scope="session")
def app():
    app = create_app()
    with app.app_context():
        transaction = db.session.begin_nested()  # execute tests in a savepoint
        yield app
        transaction.rollback()  # rollback all database changes


@pytest.fixture(scope="session")
def _session(app):
    return db.session
