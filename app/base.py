from flask import Flask
from app.views import shop_bp
from init_db import db
from app import schemas
from flask_apispec import marshal_with
from app.exceptions import BookStoreException


@marshal_with(schemas.Response)
def handle_book_store_exception(error):
    return {'code': error.code, 'error_text': error.error_text}



def add_error_handlers(app):
    app.register_error_handler(BookStoreException, handle_book_store_exception)
    


def create_app():
    flask_app = Flask(import_name=__name__)
    flask_app.config.from_pyfile('config.py', silent=True)
    db.init_app(flask_app)
    flask_app.register_blueprint(shop_bp, url_prefix='/store')
    add_error_handlers(flask_app)
    
    
    return flask_app