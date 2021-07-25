from flask import Flask
from web.app.views import shop_bp


def create_app():
    flask_app = Flask(import_name=__name__)
    flask_app.config.from_pyfile('config.py', silent=True)
    flask_app.register_blueprint(shop_bp)
    return flask_app