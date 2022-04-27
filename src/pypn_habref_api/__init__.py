from pathlib import Path

from flask import Flask
from flask_migrate import Migrate

from pypn_habref_api.env import db, ma
from pypn_habref_api.routes import routes


migrate = Migrate()


def create_app():
    app = Flask("Habref")
    app.config.from_envvar("HABREF_SETTINGS")
    ma.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db, directory=Path(__file__).parent / "migrations")
    app.register_blueprint(routes, url_prefix="/habref")
    return app
