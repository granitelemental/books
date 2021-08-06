from typing import TypedDict, Optional
from datetime import datetime



class User(TypedDict):
    first_name: str
    last_name: str
    email: str
    id: Optional[int]

class Order(TypedDict):
    id: Optional[int]
    reg_date: datetime
    user_id: int


class OrderItem(TypedDict):
    id: Optional[int]
    book_id: int
    shop_id: int
    book_quantity: int


class Shop(TypedDict):
    id: Optional[int]
    name: str
    address: str

class Book(TypedDict):
    id: Optional[int]
    name: str
    author: str
    release_date: datetime