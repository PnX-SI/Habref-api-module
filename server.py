from flask import Flask, request
from src.pypnnomenclature.env import DB
app_globals = {}


def init_app():
    if app_globals.get('app', False):
        app = app_globals['app']
    else:
        app = Flask(__name__)
    app.config.from_pyfile('config.py')
    DB.init_app(app)

    with app.app_context():
        from routes import routes
        app.register_blueprint(routes, url_prefix='/habref')
    return app


app = init_app()
if __name__ == '__main__':
    app.run()
