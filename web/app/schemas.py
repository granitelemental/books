from marshmallow import Schema, fields, validate
from web.app.constants import HttpStatus, MAX_ROWS
from db import models as mdl


class ResponseSchema(Schema):

    @staticmethod
    def dump(obj, *args, **kwargs):
        result = {'code': HttpStatus.HTTP_200_OK, 'errorText': None}
        data = obj
        if isinstance(obj, dict):
            result['errorText'] = data.pop('errorText')
            result['errorFields'] = data.pop('errorFields')
            result['errorFields'] = data.pop('errorFields')
        result['data'] = data
        return result

class LimitOffsetSchema(Schema):
    limit = fields.Integer(validate=validate.Range(min=1, max=MAX_ROWS), missing=MAX_ROWS)
    offset = fields.Integer(validate=validate.Range(min=0), missing=0)

class LimitOffsetResponseSchema(ResponseSchema, LimitOffsetSchema):
    pass


class UserResponseSchema(ResponseSchema):
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

class OrderSchema(Schema):
    id = fields.Integer(required=True, allow_none=False)
    reg_date = fields.DateTime(required=True, allow_none=False)
    user_id = fields.Integer(allow_none=False)


class OrdersResponseSchema(LimitOffsetResponseSchema, OrderSchema):
    MANY=True


class OrderItemSchema(Schema):
    book_id = fields.Integer(required=True, allow_none=False)
    shop_id = fields.Integer(required=True, allow_none=False)
    book_quantity = fields.Integer(required=True, allow_none=False)


class AddOrderRequestSchema(Schema):
    order_items = fields.Nested(OrderItemSchema, many=True)


class OrderItemsResponseSchema(ResponseSchema, OrderItemSchema):
    MANY=True

class OrderItemResponseSchema(ResponseSchema, OrderItemSchema):
    pass









