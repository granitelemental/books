
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint 
import inspect
import sys

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(60), unique=True)
    last_name = db.Column(db.String(60), unique=True)
    email = db.Column(db.String(60), unique=True)

class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    reg_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)

class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))
    book_quantity = db.Column(db.Integer)

class Shop(db.Model):
    __tablename__ = 'shop'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    address = db.Column(db.String(200), unique=True)

class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    author = db.Column(db.String(60))
    release_date = db.Column(db.DateTime)
    __table_args__ = (UniqueConstraint('author', 'name', 'release_date'),)

