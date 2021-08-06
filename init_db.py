from flask import Flask
from app.models import *

SQLALCHEMY_DATABASE_URI = (
    'mysql+pymysql://root:root@127.0.0.1:3306/db?charset=utf8'
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        db.session.commit()

