import uuid
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Cookie, Response, BackgroundTasks, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.db.database import get_db, SessionLocal
from backend.model.tables import Users, Orders, Products, Carts, ProductCart, ProductOrder
from backend.schemas.data import (
    Token, TokenData, Register, Order, Product, Test, UpdateProduct, Cart, CartDelete
)
from backend.core.config import settings

router = APIRouter(
    prefix=""
)

db = SessionLocal()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    user = db.query(Users).filter(Users.username == username).first()
    if user is not None:
        return user

def authenticate_user(username: str, password: str):
    user = get_user(username)
    print('user ' + user.username + ' ' + user.password)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception

        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception

    user = get_user(token_data.username)
    if user is None:
        raise credential_exception

    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    return current_user


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
def register(request: Register):
    username = request.username
    password = request.password
    email = request.email
    address = request.address
    admin = request.admin
    phone_number = request.phone_number

    print(password)

    if db.query(Users).filter(Users.username == username).first() is not None:
        return 'Username Already Exists'

    if db.query(Users).filter(Users.email == email).first() is not None:
        return 'Email Already Exists'

    if db.query(Users).filter(Users.phone_number == phone_number).first() is not None:
        return 'Phone Number Already Exists'

    hashed_password = get_password_hash(password)

    user = Users(
        username=username,
        password=hashed_password,
        email=email,
        phone_number=phone_number,
        address=address,
        admin=admin,
    )

    db.add(user)
    db.commit()

    db.refresh(user)

    db.add(
        Carts(
            user_id = user.id
        )
    )

    db.commit()

    return request

@router.get('/all_products')
def all_products(current_user = Depends(get_current_active_user)):
    products = db.query(Products).all()
    return products

@router.get('/my_details')
def my_details(current_user = Depends(get_current_active_user)):
    return current_user

@router.get('/my_cart')
def my_cart(current_user = Depends(get_current_active_user)):
    cart = db.query(Carts).filter(Carts.user_id == current_user.id).first()

    if cart is None:
        return 'No cart'

    all_cart_products = db.query(ProductCart).filter(ProductCart.cart_id == cart.id).all()

    return {'user': current_user, 'cart': cart, 'products': all_cart_products}

@router.get('/my_orders')
def my_orders(current_user = Depends(get_current_active_user)):
    orders = db.query(Orders).filter(Orders.user_id == current_user.id).all()
    return orders

@router.get('/order/{order_id}')
def get_order(order_id: int, current_user = Depends(get_current_active_user)):
    order = db.query(Orders).filter(Orders.id == order_id).first()

    if order.user_id != current_user.id:
        return {'user': current_user, 'products': [], 'order': None}

    all_product_orders = db.query(ProductOrder).filter(ProductOrder.order_id == order_id).all()

    return {'user': current_user, 'products': all_product_orders, 'order': order}

#Add
@router.post('/create_order')
def create_order(order: Order, current_user=Depends(get_current_active_user)):
    new_order = Orders(
        user_id = current_user.id,
        delivery_address = order.deliver_address,
        status = False
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for product_id in order.products:
        db.add(
            ProductOrder(
                product_id = int(product_id[0]),
                quantity = int(product_id[1]),
                order_id = int(new_order.id)
            )
        )

        db.commit()

    cart_id = db.query(Carts).filter(Carts.user_id == current_user.id).first().id
    all_product_carts = db.query(ProductCart).filter(ProductCart.cart_id == cart_id)

    for product in all_product_carts:
        db.delete(product)

        db.commit()

    return 'Order Was successful'

@router.post('/create_product')
def create_product(product: Product, current_user=Depends(get_current_active_user)):
    if current_user.admin is False:
        return 'Not Authorised'

    db.add(
        Products(
            name=product.name,
            size=product.size,
            price=product.price,
            description=product.description,
            photo_link=product.photo_link
        )
    )
    db.commit()

    return 'Product Created Successfully'

#Delete
@router.delete('/delete_product/{product_id}')
def delete_product(product_id: int, current_user = Depends(get_current_active_user)):
    if current_user.admin is False:
        return 'Not Authorised'

    product = db.query(Products).filter(Products.id == product_id).first()

    if product is None:
        return 'Product Does Not Exist'

    db.delete(product)
    db.commit()

    return 'Product Deleted Successfully'

#update
@router.put('/edit_product/{product_id}')
def edit_product(product_id: int, new_product: UpdateProduct, current_user = Depends(get_current_active_user)):
    if current_user.admin is False:
        return 'Not Authorised'

    product = db.query(Products).filter(Products.id == product_id).first()

    product.name = new_product.name
    product.size = new_product.size
    product.photo_link = new_product.photo_link
    product.description = new_product.description
    product.price = new_product.price

    db.commit()

    return 'Updated Successfully'

@router.put('/edit_profile')
def edit_profile(new_details: Register, current_user = Depends(get_current_active_user)):
    user = db.query(Users).filter(Users.id == current_user.id).first()

    if db.query(Users).filter(Users.username == new_details.username).first() is not None and user.username != new_details.username:
        return 'Username Already Exists'

    if db.query(Users).filter(Users.email == new_details.email).first() is not None and user.email != new_details.email:
        return 'Email Already Exists'

    if db.query(Users).filter(Users.phone_number == new_details.phone_number).first() is not None and user.phone_number != new_details.phone_number:
        return 'Phone Number Already Exists'

    user.username = new_details.username
    user.password = get_password_hash(new_details.password)
    user.email = new_details.email
    user.phone_number = new_details.phone_number
    user.address = new_details.address
    user.admin = new_details.admin

    db.commit()

    return 'Updated Successfully'

#cart section
@router.post('/add_product_to_cart')
def add_product_to_cart(product: Cart, current_user = Depends(get_current_active_user)):
    db.add(
        ProductCart(
            product_id = product.product_id,
            quantity = product.quantity,
            cart_id = db.query(Carts).filter(Carts.user_id == current_user.id).first().id
        )
    )

    db.commit()

    return 'Product Added'

@router.post('/edit_quantity')
def edit_quantity(product: Cart, current_user = Depends(get_current_active_user)):
    product_to_edit = db.query(ProductCart).filter(ProductCart.cart_id == current_user.id, ProductCart.product_id == product.product_id).first()

    if product_to_edit is None:
        return 'No such product found'

    product_to_edit.quantity = product.quantity

    db.commit()

    return 'Quantity Edited'

@router.post('/remove_product')
def remove_product(product: CartDelete, current_user = Depends(get_current_active_user)):
    product_to_delete = db.query(ProductCart).filter(ProductCart.cart_id == current_user.id, ProductCart.product_id == product.product_id).first()

    if product_to_delete is None:
        return 'No such product found'

    db.delete(product_to_delete)
    db.commit()

    return 'Product Deleted'

#special tests
@router.get("/get_data")
def get_data():
    users = db.query(Users).all()
    productorder = db.query(ProductOrder).all()
    return productorder

@router.post("/post_data")
def post_data(data: Test):
    db.add(
        ProductOrder(
            product_id = data.product_id,
            quantity = data.quantity,
            order_id = data.order_id
        )
    )
    db.commit()

    return data
