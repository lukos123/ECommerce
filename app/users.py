import re

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models import User, UserType


def is_valid_email(email):
    # Basic regex for email validation
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(regex, email):
        return True
    else:
        return False


bp = Blueprint('users', __name__)


@bp.route('', methods=['GET'])
@bp.route('/', methods=['GET'])
def get_user_profiles():
    users = User.query.all()
    return jsonify([user.to_dict_profile() for user in users])


@bp.route('/main', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user: UserType = db.session.get(User, user_id)
    if not user:
        return jsonify({}), 404
    return jsonify(user.to_dict())


@bp.route('/main', methods=['PUT'])
@bp.route('/', methods=['PUT'])
@bp.route('', methods=['PUT'])
@jwt_required()
def set_user():
    user_id = get_jwt_identity()
    user: UserType = db.session.get(User, user_id)
    data = request.get_json()
    if not user:
        return jsonify({}), 404
    username = data.get("username", user.username)
    email = data.get("email", user.email)
    password = data.get("password")
    description = data.get("description", user.description)
    if len(password) > 5:
        user.set_password(password)
    else:
        return jsonify({'message': 'Password is small'}), 401
    if len(username) > 5:
        user.username = username
    else:
        return jsonify({'message': 'Username is small'}), 401

    if is_valid_email(email):
        user.email = email
    else:
        return jsonify({'message': 'Email is not valid'}), 401
    user.description = description

    db.session.commit()
    return jsonify(user.to_dict())


@bp.route('/<int:id>', methods=['GET'])
def get_profile(id):
    user: UserType = db.session.get(User, id)
    if not user:
        return jsonify({}), 404
    return jsonify(user.to_dict_profile())
