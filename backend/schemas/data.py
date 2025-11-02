from symtable import Class
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str or None = None


class User(BaseModel):
    username: str
    email: str or None = None
    full_name: str or None = None
    disabled: bool or None = None

class Register(BaseModel):
    username: str
    password: str
    email: str
    address: str
    admin: bool
    phone_number: str

class Order(BaseModel):
    deliver_address: str
    products: List[List[int]]

class Product(BaseModel):
    name: str
    price: int
    description: str
    size: str
    photo_link: str

class Test(BaseModel):
    product_id: int
    order_id: int
    quantity: int

class UpdateProduct(BaseModel):
    name: str
    price: int
    description: str
    photo_link: str
    size: str

class Cart(BaseModel):
    product_id: int
    quantity: int

class CartDelete(BaseModel):
    product_id: int