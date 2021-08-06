from flask_apispec import doc, use_kwargs, marshal_with
from sqlalchemy import desc
from datetime import datetime, date

from typing import Callable, Dict, List
from app import models as mdl
from flask import Blueprint, request, jsonify

from app import schemas, constants
from app.exceptions import BookStoreException
from app.constants import HttpStatus, MAX_ROWS, ErrorMessages
from app.types import User, Order, OrderItem
from sqlalchemy.exc import IntegrityError
import logging


shop_bp = Blueprint('shop', __name__)

@shop_bp.app_errorhandler(422)
@shop_bp.app_errorhandler(400)
def handle_error(err):
    headers = err.data.get('headers', None)
    try:
        error_fields = [
            {key: value}
            for key, value in
            err.data['messages']['json'].items()
            ]
    except AttributeError:
        error_fields = ['Invalid request.']
    if headers:
        return jsonify({'errorFields': error_fields}), err.code, headers
    else:
        return jsonify({'errorFields': error_fields}), err.code


def log(func):
    def wrapped(*args, **kwargs):
        logging.info(
            f'{request.method}, {request.path}', {'data': request.data}
        )
        response = func(*args, **kwargs)
        logging.info(
            f'{request.method}, {request.path}', {
                'code': response['code'],
                'error_text': response.get('errorText'),
                'error_fields': response.get('errorFields')
            }
        )
    return wrapped


def handle_integrity_error(error_message: str):
    def decorator(funct: Callable):
        def wrapped(*args, **kwargs):
            try:
                result = funct(*args, **kwargs)
            except IntegrityError:
                raise BookStoreException(
                    code=HttpStatus.HTTP_400_BAD_REQUEST,
                    error_text=error_message
                )
            return result
        return wrapped
    return decorator


class BookStoreController:

    @staticmethod
    @handle_integrity_error(ErrorMessages.SHOP_ALREADY_EXISTS)
    def add_book(name: str, author: str, release_date: date):
        book = mdl.Book(
            name = name,
            author = author,
            release_date = release_date,
        )
        mdl.db.session.add(book)
        mdl.db.session.commit()
        return book.id


    @staticmethod
    def get_book(book_id: int):
        book = mdl.Book.query.filter_by(id=book_id).one_or_none()
        if book is None:
            raise BookStoreException(
                code=HttpStatus.HTTP_404_NOT_FOUND,
                error_text=ErrorMessages.BOOK_NOT_FOUND.format(book_id),
            )
        return book

    @staticmethod
    def get_books():
        books = mdl.Book.query.all()
        return books



    @staticmethod
    @handle_integrity_error(ErrorMessages.SHOP_ALREADY_EXISTS)
    def add_shop(name: str, address: str):
        shop = mdl.Shop(
            name = name,
            address = address,
        )
        mdl.db.session.add(shop)
        mdl.db.session.commit()
        return shop.id


    @staticmethod
    def get_shops():
        shops = mdl.Shop.query.all()
        return shops

    
    @staticmethod
    def get_shop(shop_id: int):
        shop = mdl.Shop.query.filter_by(id=shop_id).one_or_none()
        if shop is None:
            raise BookStoreException(
                code=HttpStatus.HTTP_404_NOT_FOUND,
                error_text=ErrorMessages.SHOP_NOT_FOUND.format(shop_id),
            )
        return shop

    
    @staticmethod
    @handle_integrity_error(ErrorMessages.USER_ALREADY_EXISTS)
    def add_user(first_name: str, last_name: str, email: str) -> int:
        user = mdl.User(
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
        mdl.db.session.add(user)
        mdl.db.session.commit()
        return user.id


    @staticmethod
    def get_user(user_id: int) -> User:
        user = (
            mdl.User.query
                .filter_by(id=user_id)
                .with_entities(
                    mdl.User.first_name,
                    mdl.User.last_name,
                    mdl.User.email,
                )
                .one_or_none()
        )
        if user is None:
            raise BookStoreException(
                code=HttpStatus.HTTP_404_NOT_FOUND,
                error_text=ErrorMessages.USER_NOT_FOUND.format(user_id),
            )
        return user


    @staticmethod
    def get_users() -> List[User]:
        users = (
            mdl.User.query
                .with_entities(
                mdl.User.first_name,
                mdl.User.last_name,
                mdl.User.email,
                mdl.User.id,
            )
                .all()
        )
        return [
            {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'id': user.id,
            }
            for user in users
        ]

    @staticmethod
    def get_orders(user_id: int, limit: int=0, offset: int=MAX_ROWS) -> List[Order]:
        orders = (
            mdl.Order.query
                .filter_by(user_id=user_id)
                .with_entities(
                    mdl.Order.id,
                    mdl.Order.reg_date,
                )
                .order_by(desc(mdl.Order.reg_date))
                .limit(limit)
                .offset(offset)
                .all()
        )
        return orders

    @staticmethod
    def get_order_items(order_id: int, limit: int=0, offset: int=MAX_ROWS) -> List[OrderItem]:
        order_items = (
            mdl.OrderItem.query
                .join(
                    mdl.Book, mdl.Book.id == mdl.OrderItem.book_id
                ).join(
                    mdl.Shop, mdl.Shop.id == mdl.OrderItem.shop_id
                )
                .filter(mdl.OrderItem.order_id==order_id)
                .order_by(
                    desc(mdl.OrderItem.shop_id),
                    desc(mdl.OrderItem.book_id),
                )
                .limit(limit)
                .offset(offset)
                .with_entities(
                    mdl.Shop.name.label('shop_name'),
                    mdl.Shop.address,
                    mdl.Book.name.label('book_name'),
                    mdl.Book.author,
                    mdl.Book.release_date,
                    mdl.OrderItem.book_quantity,
                )
                .all()
        )
        if not order_items:
            raise BookStoreException(
                code=HttpStatus.HTTP_404_NOT_FOUND,
                error_text=ErrorMessages.ORDER_EMPTY_OR_NOT_FOUND.format(order_id),
            )
        return order_items

    @staticmethod
    @handle_integrity_error(ErrorMessages.CAN_NOT_ADD_ORDER)
    def add_order(user_id: int, order_items: List[OrderItem]) -> None:
        order = mdl.Order(
            reg_date = datetime.utcnow().date(),
            user_id = user_id,
        )
        try:
            mdl.db.session.add(order)
        except IntegrityError as error:
            raise BookStoreException(
                code=HttpStatus.HTTP_400_BAD_REQUEST,
                error_text=str(error)
            )

        mdl.db.session.flush()

        mdl.db.session.bulk_save_objects(
            [
                mdl.OrderItem(
                    order_id=order.id,
                    book_quantity=item['book_quantity'],
                    book_id=item['book_id'],
                    shop_id=item['shop_id'],
                )
                for item in order_items
            ]
        )
        mdl.db.session.commit()
        return order.id


@doc(description='Получить список ручек')
@shop_bp.route('/', methods=['GET'])
def get_index():
    return {
        '1': '/users/<int:user_id>'
    }   
    

@doc(description='Добавить юзера')
@shop_bp.route('/users', methods=['POST'])
@use_kwargs(schemas.User())
@marshal_with(schemas.AddUserResponse, code=constants.HttpStatus.HTTP_200_OK)
def add_user(first_name: str, last_name: str, email: str):
    return {
        'user_id': BookStoreController.add_user(
            first_name=first_name, last_name=last_name, email=email
        )
    }


@doc(description='Получить данные юзера')
@shop_bp.route('/users/<int:user_id>', methods=['GET'])
@marshal_with(schemas.UserResponse())
def get_user(user_id: int):
    return BookStoreController.get_user(user_id)


@doc(description='Получить список юзеров')
@shop_bp.route('/users', methods=['GET'])
@marshal_with(schemas.UsersResponse())
def get_users():
    return {'users': BookStoreController.get_users()}


@doc(description='Получить заказы юзера')
@shop_bp.route('/users/<int:user_id>/orders', methods=['GET'])
@use_kwargs(schemas.LimitOffset())
@marshal_with(schemas.OrdersResponse)
def get_user_orders(user_id: int, limit: int, offset: int):
    return {
        'orders': BookStoreController.get_orders(
            user_id=user_id, 
            limit=limit, 
            offset=offset,
            )
        }


@doc(description='Получение данных определенного заказа')
@shop_bp.route('/orders/<int:order_id>', methods=['GET'])
@use_kwargs(schemas.LimitOffset())
@marshal_with(schemas.OrderResponse)
def get_order_details(order_id: int, limit: int, offset: int):
    return {
        'order_id': order_id,
        'order_items': BookStoreController.get_order_items(
            order_id=order_id, 
            limit=limit, 
            offset=offset,
        )
    }


@doc(description='Добавление нового заказа')
@shop_bp.route('/users/<int:user_id>/orders', methods=['POST'])
@use_kwargs(schemas.AddOrderRequest())
@marshal_with(schemas.AddOrderResponse)
def add_order(user_id: int, order_items: List[OrderItem]):
    return {
        'order_id': BookStoreController.add_order(
            user_id=user_id, 
            order_items=order_items,
            )
        }


@doc(description='Добавление нового магазина')
@shop_bp.route('/shops', methods=['POST'])
@use_kwargs(schemas.ShopRequest())
@marshal_with(schemas.ShopResponse)
def add_shop(name: str, address: str):
    return {'id': BookStoreController.add_shop(name=name, address=address)}


@doc(description='Просмотреть все магазины')
@shop_bp.route('/shops', methods=['GET'])
@marshal_with(schemas.ShopsResponse)
def get_shops():
    return {'shops': BookStoreController.get_shops()}



@doc(description='Просмотреть магазин')
@shop_bp.route('/shops/<int:shop_id>', methods=['GET'])
@marshal_with(schemas.ShopResponse)
def get_shop(shop_id: int):
    return BookStoreController.get_shop(shop_id)



@doc(description='Добавление новой книги')
@shop_bp.route('/books', methods=['POST'])
@use_kwargs(schemas.BookRequest())
@marshal_with(schemas.AddBookResponse)
def add_book(author: str, name: str, release_date: str):
    return {
        'book_id': BookStoreController.add_book(
            author=author, 
            name=name, 
            release_date=release_date,
            )
    }


@doc(description='Просмотр книги')
@shop_bp.route('/books/<int:book_id>', methods=['GET'])
@marshal_with(schemas.BookResponse)
def get_book(book_id: int):
    return BookStoreController.get_book(book_id)


@doc(description='Просмотр всех книг')
@shop_bp.route('/books', methods=['GET'])
@marshal_with(schemas.BooksResponse)
def get_books():
    return {'books': BookStoreController.get_books()}