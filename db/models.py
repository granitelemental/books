
from flask_sqlalchemy import SQLAlchemy, declarative_base


db = SQLAlchemy()
Model = declarative_base()


class User(Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(60), unique=True)
    last_name = db.Column(db.String(60), unique=True)
    email = db.Column(db.String(60), unique=True)
    orders = db.relationship('Order', order_by='desc(Order.reg_date)', lazy='dynamic')

class Order(Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    user = db.relationship('User')
    order_items = db.relationship('OrderItem', )

class OrderItem(Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))
    book_quantity = db.Column(db.Integer)

class Shop(Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    address = db.Column(db.String(200), unique=True)

class Book(Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    author = db.Column(db.String(60), unique=True)
    release_date = db.Column(db.DateTime)


