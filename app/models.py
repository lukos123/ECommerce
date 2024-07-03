import datetime
from typing import List

from sqlalchemy.orm import backref, Mapped
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token

from . import db


class User(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email: str = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash: str = db.Column(db.String(256), nullable=False)
    description: str = db.Column(db.Text, default="")
    permission: str = db.Column(db.String(10), default="user")
    products: Mapped[List['Product']] = db.relationship(back_populates='user')
    comments: Mapped[List['Comment']] = db.relationship(back_populates='user')
    cart_items: Mapped[List['CartItem']] = db.relationship(back_populates='user')
    orders: Mapped[List['Order']] = db.relationship(back_populates='user')
    cart_item_groups: Mapped[List['CartItemGroup']] = db.relationship(back_populates='user')
    notifications: Mapped[List['Notification']] = db.relationship(back_populates='supplier')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_tokens(self):
        access_token = create_access_token(identity=self.id)
        refresh_token = create_refresh_token(identity=self.id)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "description": self.description,
            "email": self.email,
            "products": [i.to_dict() for i in self.products],
            "comments": [i.to_dict() for i in self.comments],
            "orders": [i.to_dict() for i in self.orders],
            "notifications": [i.to_dict() for i in self.notifications],
            "cart_item_groups": [i.to_dict() for i in self.cart_item_groups],

        }

    def to_dict_profile(self):
        return {
            "id": self.id,
            "username": self.username,
            "description": self.description,
            "products": [i.to_dict() for i in self.products],

        }


# Type classes for type hinting and autocompletion
class UserType:
    """
    Этот класс используется только для аннотации типов и подсказок в PyCharm.
    Объекты этого класса не создаются в реальном коде.
    """
    id: int
    username: str
    email: str
    password_hash: str
    permission: str
    description: str
    products: List['ProductType']
    comments: List['CommentType']
    cart_items: List['CartItemType']
    orders: List['OrderType']
    cart_item_groups: List['CartItemGroupType']
    notifications: List['NotificationType']

    def set_password(self, password: str):
        pass

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    def get_tokens(self):
        access_token = create_access_token(identity=self.id)
        refresh_token = create_refresh_token(identity=self.id)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }

    def to_dict_profile(self):
        return {
            "id": self.id,
            "username": self.username,
            "products": [i.to_dict() for i in self.products],

        }


class Product(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name: str = db.Column(db.String(128), nullable=False)
    image: str = db.Column(db.String(128), nullable=True)
    price: int = db.Column(db.Float, nullable=False)
    description: str = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.UTC))
    user: Mapped['User'] = db.relationship(back_populates='products')
    comments: Mapped[List['Comment']] = db.relationship(back_populates='product')
    cart_items: Mapped[List['CartItem']] = db.relationship(back_populates='product')

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "created_at": self.created_at,
            "image": "" if self.image is None else self.image
        }


# Type classes for type hinting and autocompletion
class ProductType:
    id: int
    user_id: int
    name: str
    image: str
    price: int
    description: str
    created_at: str
    user: UserType
    comments: List['CommentType']
    cart_items: List['CartItemType']

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,

        }


class Comment(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    product_id: int = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id: int = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text: str = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.UTC))
    product: Mapped['Product'] = db.relationship(back_populates='comments')
    user: Mapped['User'] = db.relationship(back_populates='comments')

    def to_dict(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "text": self.text,
            "created_at": self.created_at

        }


# Type classes for type hinting and autocompletion
class CommentType:
    id: int
    product_id: int
    user_id: int
    text: str
    created_at: str
    product: ProductType
    user: UserType

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.text,

        }


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cart_group_id = db.Column(db.Integer, db.ForeignKey('cart_item_group.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    user: Mapped['User'] = db.relationship(back_populates='cart_items')
    product: Mapped['Product'] = db.relationship(back_populates='cart_items')
    cart_group: Mapped['CartItemGroup'] = db.relationship(back_populates='cart_items')

    def to_dict(self):
        return {
            "id": self.id,
            "cart_group_id": self.cart_group_id,
            "product_id": self.product_id,
            "status": self.status,
            "product": self.product.to_dict(),
            "name": self.product.name,
            "quantity": self.quantity

        }


# Type classes for type hinting and autocompletion
class CartItemType:
    id: int
    user_id: int
    status: str | None
    product_id: int
    cart_group_id: int
    quantity: int
    # user: UserType
    product: ProductType

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.quantity,

        }


class CartItemGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user: Mapped['User'] = db.relationship(back_populates='cart_item_groups')
    order: Mapped['Order'] = db.relationship(back_populates="cart_group")  # one to one
    cart_items: Mapped[List['CartItem']] = db.relationship(back_populates="cart_group")

    def to_dict(self):
        return {
            "id": self.id,
            "cart_items": [cart_item.to_dict() for cart_item in self.cart_items],
            "user_id": self.user_id,
            "main": self.order is None,
        }


# Type classes for type hinting and autocompletion
class CartItemGroupType:
    id: int
    user_id: int
    user: UserType
    cart_items: List['CartItemType']
    order: 'OrderType | None'

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,

        }


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    delivery = db.Column(db.String(50), default="WorldDelivery")
    status = db.Column(db.String(50), default="Not Ready")
    delivery_to = db.Column(db.String(50), nullable=True)
    cart_item_group_id = db.Column(db.Integer, db.ForeignKey('cart_item_group.id'), nullable=False)
    cart_group: Mapped['CartItemGroup'] = db.relationship(back_populates="order")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user: Mapped['User'] = db.relationship(back_populates='orders')
    notifications: Mapped[List['Notification']] = db.relationship(back_populates='order')

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "delivery": self.delivery,
            "delivery_to": self.delivery_to,
            "status": self.status,
            "cart_item_group_id": self.cart_item_group_id,
            "cart_group": self.cart_group.to_dict(),
        }


# Type classes for type hinting and autocompletion
class OrderType:
    id: int
    delivery: str
    status: str
    delivery_to: str | None
    cart_item_group_id: int
    user_id: int
    user: UserType
    cart_group: CartItemGroupType
    notifications: List['NotificationType']

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
        }


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    supplier: Mapped['User'] = db.relationship(back_populates='notifications')
    order: Mapped['Order'] = db.relationship(back_populates='notifications')

    def to_dict(self):
        order = self.order.to_dict()
        temp = []
        found_sent_all = True
        found_made_all = True
        found_wait_all = True
        for item in order["cart_group"]["cart_items"]:
            if item["product"]["user_id"] == self.supplier_id:
                temp.append(item)
            if item["status"] != "Sent":
                found_sent_all = False
            if item["status"] != "Made":
                found_made_all = False
            if item["status"] != "Wait for send delivery":
                found_wait_all = False
        if found_made_all:
            order["status"] = "All made"
        if found_sent_all:
            order["status"] = "All sent"
        if found_wait_all:
            order["status"] = "Wait for send delivery"
        order["cart_group"]["cart_items"] = temp
        return {
            "id": self.id,
            "supplier_id": self.supplier_id,
            "order_id": self.order_id,
            "order": order
        }


# Type classes for type hinting and autocompletion
class NotificationType:
    id: int
    supplier_id: int
    supplier: UserType
    order: OrderType

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.supplier_id,

        }
