from typing import NamedTuple, List
from datetime import datetime



class User(NamedTuple):
    first_name: str
    last_name: str
    email: str

class Order(NamedTuple):
    id: int
    reg_date: datetime
    user_id: int


class OrderItem(NamedTuple):
    id: int
    book_id: int
    shop_id: int
    book_quantity: int
