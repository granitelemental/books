from marshmallow import Schema, fields, validate, pre_dump, post_dump
from app.constants import HttpStatus, MAX_ROWS
from app import models as mdl
from copy import deepcopy


class Response(Schema):
    error_text = None
    error_fields = None

    @pre_dump
    def extract_data(self, response, **kwargs):
        if isinstance(response, dict):
            self.error_text = response.pop('error_text', None)
            self.error_fields = response.pop('error_fields', [])
        return response

    @post_dump
    def add_error_info(self, data, **kwargs):
        result = {
            'code': HttpStatus.HTTP_200_OK,
            'data': data,
        }
        if self.error_text is not None:
            result.update({'errorText': self.error_text})
        if self.error_fields:
            result.update({'errorFields': deepcopy(self.error_fields)})
            
        self.error_text = None
        self.error_fields = None
        return result


class LimitOffset(Schema):
    limit = fields.Integer(validate=validate.Range(min=1, max=MAX_ROWS), missing=MAX_ROWS)
    offset = fields.Integer(validate=validate.Range(min=0), missing=0)

class LimitOffsetResponse(Response, LimitOffset):
    pass


class User(Schema):
    last_name = fields.String(
        validate=validate.Length(max=mdl.User.last_name.type.length),
        allow_none=False,
        required=True,
    )
    first_name = fields.String(
        validate=validate.Length(max=mdl.User.first_name.type.length),
        allow_none=False,
        required=True,
    )
    email = fields.String(
        validate=validate.Length(max=mdl.User.email.type.length),
        allow_none=False,
        required=True,
    )
    id = fields.Integer(required=False, allow_none=False)



class UsersResponse(Response):
    users = fields.Nested(User, many=True)


class UserResponse(User, Response):
    pass


class AddUserResponse(Response):
    user_id = fields.Integer(required=True, nullable=False)


class Order(Schema):
    id = fields.Integer(required=True, allow_none=False)
    reg_date = fields.DateTime(required=True, allow_none=False)
    user_id = fields.Integer(allow_none=False)


class OrdersResponse(LimitOffsetResponse):
    orders = fields.Nested(Order, many=True, required=True)


class OrderItem(Schema):
    book_name = fields.String(required=True, allow_none=False)
    author = fields.String(required=True, allow_none=False)
    release_date = fields.Date(required=True, allow_none=False)
    shop_name = fields.String(required=True, allow_none=False)
    address = fields.String(required=True, allow_none=False)
    book_quantity = fields.Integer(required=True, allow_none=False)


class AddOrderItem(Schema):
    book_id = fields.Integer(required=True, allow_none=False)
    book_quantity = fields.Integer(required=True, allow_none=False)
    shop_id = fields.Integer(required=True, allow_none=False)


class AddOrderRequest(Schema):
    order_items = fields.Nested(AddOrderItem, many=True)


class AddOrderResponse(Schema):
    order_id = fields.Integer(required=True, nullable=False)



class OrderResponse(LimitOffsetResponse):
    order_id = fields.Integer(required=True, nullable=False)
    order_items = fields.Nested(OrderItem, many=True)


class Shop(Schema):
    id = fields.Integer(requred=False)
    name = fields.String(required=True, nullable=False)
    address = fields.String(required=True, nullable=False)


class ShopRequest(Shop):
    pass


class ShopResponse(Response, Shop):
    pass


class ShopsResponse(Response):
    shops = fields.Nested(Shop, many=True, required=True)


class Book(Schema):
    id = fields.Integer(required=False, nullable=False)
    name = fields.String(required=True, nullable=False)
    author = fields.String(required=True, nullable=False)
    release_date = fields.Date(required=True, nullable=False)

class BookRequest(Book):
    pass


class BookResponse(Response, Book):
    pass


class BooksResponse(Response):
    books = fields.Nested(Book, many=True, required=True)

class AddBookResponse(Response):
    book_id = fields.Integer(required=True, nullable=False)











