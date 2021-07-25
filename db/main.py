from flask import Flask
import os
from db.models import db

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_DATABASE = os.getenv('DB_DATABASE')
DB_PORT = os.getenv('DB_PORT')
DB_HOST = os.getenv('DB_HOST')


if not all([DB_USER, DB_PASSWORD, DB_DATABASE, DB_PORT]):
    raise SystemExit('Отсутствует обязательные параметры подключения к базе')

SQLALCHEMY_DATABASE_URI = (
    f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}?charset=utf8'
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI


if __name__ == '__main__':
    db.init_app(app)
    db.create_all()