from datetime import timedelta

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

from app import db
from app.models import User, UserType, CartItemGroup
import re

bp = Blueprint('auth', __name__)


def is_valid_email(email):
    # Basic regex for email validation
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(regex, email):
        return True
    else:
        return False


@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']
    user_exist = User.query.filter_by(username=username).first()
    email_exist = User.query.filter_by(email=email).first()
    if user_exist or email_exist:
        return jsonify({'message': 'User already exists'}), 400
    name_valid = len(username) > 5
    if not name_valid:
        return jsonify({'message': 'Name is short'}), 400
    email_valid = is_valid_email(email)
    if not email_valid:
        return jsonify({'message': 'Email is not valid'}), 400
    if len(password) < 5:
        return jsonify({'message': 'Password is small'}), 400

    user: UserType = User(username=username, email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()
    cart_main_item_group = CartItemGroup(user_id=user.id)
    db.session.add(cart_main_item_group)
    db.session.commit()

    tokens = user.get_tokens()
    return jsonify(tokens), 201


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        user = User.query.filter_by(email=username).first()
        if user is None or not user.check_password(password):
            return jsonify({'message': 'Invalid credentials'}), 401

    tokens = user.get_tokens()
    return jsonify(tokens), 200


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user, expires_delta=timedelta(minutes=15))
    return jsonify({'access_token': access_token}), 200
