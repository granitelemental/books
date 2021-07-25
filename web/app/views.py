from flask_apispec import doc, use_kwargs, marshal_with
from sqlalchemy import desc
from datetime import datetime

from typing import Dict, List
from db import models as mdl
from flask import Blueprint, request
from web.app.schemas import (
    UserResponseSchema,
    OrdersResponseSchema,
    AddOrderRequestSchema,
    OrderItemResponseSchema,
    LimitOffsetSchema,
    ResponseSchema,
)
from web.app.exceptions import BookStoreException
from web.app.constants import HttpStatus, MAX_ROWS, ErrorMessages
from web.app.types import User, Order, OrderItem
from sqlalchemy.exc import IntegrityError
import logging


shop_bp = Blueprint('shop', __name__)

@shop_bp.errorhandler(code_or_exception=BookStoreException)
@marshal_with(ResponseSchema)
def handle_book_store_exception(error):
    return {'code': error.code, 'error_text': error.error_text}


def log(func):
    def wrapped(*args, **kwargs):
        logging.info(
            f'{request.method}, {request.path}', {'data': request.date}
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



class BookStoreController:
    @staticmethod
    def get_user(user_id: int) -> User:
        user = (
            mdl.User.query
                .get(user_id)
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
                error_text=ErrorMessages.USER_NOT_FOUND,
            )
        return user

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
            mdl.OrderItem
                .filter_by(order_id=order_id)
                .limit(limit)
                .offset(offset)
                .order_by(
                    desc(mdl.OrderItem.shop_id),
                    desc(mdl.OrderItem.book_id),
                )
                .with_entities(
                    mdl.OrderItem.book_id,
                    mdl.OrderItem.book_quantity,
                    mdl.OrderItem.shop_id,
                )
                .all()
        )
        if not order_items:
            raise BookStoreException(
                code=HttpStatus.HTTP_404_NOT_FOUND,
                error_text=ErrorMessages.ORDER_EMPTY_OR_NOT_FOUND,
            )
        return order_items

    @staticmethod
    def add_order(user_id: int, order_items: List[Dict]) -> None:
        order = mdl.Order(
            reg_date = datetime.utcnow(),
            user_id = user_id,
        )
        try:
            mdl.session.add(order)
        except IntegrityError as error:
            raise BookStoreException(
                code=HttpStatus.HTTP_400_BAD_REQUEST,
                error_text=str(error)
            )

        mdl.session.flush()

        mdl.session.bulk_save_objects(
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
        mdl.session.commit()



@doc(description='Получить данные юзера')
@shop_bp.route('users/<int:user_id>', methods=['GET'])
@marshal_with(UserResponseSchema)
def get_user(user_id: int):
    return BookStoreController.get_user(user_id)


@doc(description='Получить заказы юзера')
@shop_bp.route('users/<int:user_id>/orders', methods=['GET'])
@use_kwargs(LimitOffsetSchema)
@marshal_with(OrdersResponseSchema)
def get_user(user_id: int, limit: int, offset: int):
    return BookStoreController.get_orders(user_id=user_id, limit=limit, offset=offset)


@doc(description='Получение данных определенного заказа')
@shop_bp.route('orders/<int:order_id>', methods=['GET'])
@use_kwargs(LimitOffsetSchema)
@marshal_with(OrderItemResponseSchema)
def get_user(order_id: int, limit: int, offset: int):
    return BookStoreController.get_order_items(order_id=order_id, limit=limit, offset=offset)


@doc(description='Добавление нового заказа')
@shop_bp.route('orders/<int:order_id>', methods=['POST'])
@use_kwargs(AddOrderRequestSchema)
@marshal_with(ResponseSchema)
def get_user(order_id: int, limit: int, offset: int):
    return BookStoreController.add_order(order_id=order_id, limit=limit, offset=offset)

