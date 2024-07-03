import re

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models import User, UserType

bp = Blueprint('notification', __name__)


@bp.route('', methods=['GET'])
@bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    user_id = get_jwt_identity()
    users: UserType = User.query.filter_by(id=user_id).first_or_404()

    return jsonify([notification.to_dict() for notification in users.notifications])


@bp.route('/made', methods=['GET'])
@jwt_required()
def get_notifications_made():
    user_id = get_jwt_identity()
    user: UserType = User.query.filter_by(id=user_id).first_or_404()
    arr = []
    for notification in user.notifications:
        notif = notification.to_dict()
        if notif["order"]["status"] == "All made":
            arr.append(notif)

    return jsonify(arr)


@bp.route('/not_made', methods=['GET'])
@jwt_required()
def get_notifications_not_made():
    user_id = get_jwt_identity()
    user: UserType = User.query.filter_by(id=user_id).first_or_404()
    arr = []
    for notification in user.notifications:
        notif = notification.to_dict()
        if notif["order"]["status"] == "Wait for send delivery" or notif["order"]["status"] == "All sent":
            arr.append(notif)

    return jsonify(arr)


@bp.route('/sent', methods=['GET'])
@jwt_required()
def get_notifications_sent():
    user_id = get_jwt_identity()
    user: UserType = User.query.filter_by(id=user_id).first_or_404()
    arr = []
    for notification in user.notifications:
        notif = notification.to_dict()
        if notif["order"]["status"] == "All sent":
            arr.append(notif)

    return jsonify(arr)


@bp.route('/not_sent', methods=['GET'])
@jwt_required()
def get_notifications_not_sent():
    user_id = get_jwt_identity()
    user: UserType = User.query.filter_by(id=user_id).first_or_404()
    arr = []
    for notification in user.notifications:
        notif = notification.to_dict()
        if notif["order"]["status"] == "Wait for send delivery":
            arr.append(notif)

    return jsonify(arr)


