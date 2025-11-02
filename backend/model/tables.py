from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.db.database import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, index=True, unique=True, nullable=False)
    address = Column(String)
    admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    phone_number = Column(String, index=True, unique=True, nullable=False)

    orders = relationship("Orders", back_populates="user")
    carts = relationship("Carts", back_populates="user")


class Orders(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ordered_at = Column(DateTime(timezone=True), server_default=func.now())
    delivery_address = Column(String)
    status = Column(String)
    delivery_link = Column(String)

    user = relationship("Users", back_populates="orders")
    productorder = relationship("ProductOrder", back_populates="order")


class Products(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    price = Column(Integer, nullable=False)
    size = Column(String, nullable=False)
    description = Column(String)
    photo_link = Column(String)

    productcart = relationship("ProductCart", back_populates="product")
    productorder = relationship("ProductOrder", back_populates="product")


class Carts(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("Users", back_populates="carts")
    productcart = relationship("ProductCart", back_populates="cart")


class ProductCart(Base):
    __tablename__ = "productcart"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    cart_id = Column(Integer, ForeignKey("carts.id"))
    quantity = Column(Integer)

    product = relationship("Products", back_populates="productcart")
    cart = relationship("Carts", back_populates="productcart")


class ProductOrder(Base):
    __tablename__ = "productorder"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    order_id = Column(Integer, ForeignKey("orders.id"))
    quantity = Column(Integer)

    product = relationship("Products", back_populates="productorder")
    order = relationship("Orders", back_populates="productorder")
