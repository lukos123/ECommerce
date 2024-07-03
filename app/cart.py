from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import CartItem, Product, CartItemType, CartItemGroup, CartItemGroupType, Order, User, UserType, \
    OrderType, Notification

bp = Blueprint('cart', __name__)


@bp.route('/', methods=['GET'])
@bp.route('', methods=['GET'])
@jwt_required()
def get_carts():
    user_id = get_jwt_identity()
    cart_groups: list[CartItemGroupType] = CartItemGroup.query.filter_by(user_id=user_id).all()

    return jsonify([cart_group.to_dict() for cart_group in cart_groups])


@bp.route('/main', methods=['GET'])
@jwt_required()
def get_main_cart():
    user_id = get_jwt_identity()
    cart_group: CartItemGroupType = CartItemGroup.query.filter_by(user_id=user_id).filter(
        CartItemGroup.order == None).first()
    return jsonify(cart_group.to_dict())


@bp.route('/main', methods=['POST'])
@bp.route('/', methods=['POST'])
@bp.route('', methods=['POST'])
@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()
    data = request.get_json()
    product_id = data['product_id']
    quantity = data['quantity']

    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({}), 404
    cart_item_main_group: CartItemGroupType = CartItemGroup.query.filter(CartItemGroup.user_id == user_id,
                                                                         CartItemGroup.order == None).first_or_404()
    cart_item: CartItemType = CartItem.query.filter_by(user_id=user_id, product_id=product_id,
                                                       cart_group_id=cart_item_main_group.id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity,
                             cart_group_id=cart_item_main_group.id)
        cart_item_main_group.cart_items.append(cart_item)
    db.session.commit()
    return jsonify(cart_item.to_dict()), 201


@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_cart_item(id):
    user_id = get_jwt_identity()
    data = request.get_json()
    cart_item = CartItem.query.filter_by(id=id, user_id=user_id).first_or_404()
    cart_item.quantity = data['quantity']
    db.session.commit()
    return jsonify(cart_item.to_dict())


@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_cart_item(id):
    user_id = get_jwt_identity()
    cart_item_main_group: CartItemGroupType = CartItemGroup.query.filter(CartItemGroup.user_id == user_id,
                                                                         CartItemGroup.order == None).first_or_404()
    cart_item: CartItemType = CartItem.query.filter_by(id=id, user_id=user_id,
                                                       cart_group_id=cart_item_main_group.id).first_or_404()
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Cart item deleted'})


@bp.route('/order', methods=['POST'])
@jwt_required()
def order_start():
    user_id = get_jwt_identity()
    cart_item_main_group: CartItemGroupType = CartItemGroup.query.filter(CartItemGroup.user_id == user_id,
                                                                         CartItemGroup.order == None).first_or_404()
    order_now = Order(cart_item_group_id=cart_item_main_group.id, user_id=user_id)
    cart_item_main_group.order = order_now
    cart_item_main_new = CartItemGroup(user_id=user_id)
    db.session.add(cart_item_main_new)
    db.session.commit()
    return jsonify({'message': 'Start order'})


@bp.route('/order/all', methods=['GET'])
@jwt_required()
def order_all():
    user_id = get_jwt_identity()
    user: UserType = User.query.filter_by(id=user_id).first_or_404()

    return jsonify([order.to_dict() for order in user.orders])


@bp.route('/order/<int:id>', methods=['GET'])
@jwt_required()
def order_with_id(id):
    user_id = get_jwt_identity()
    order = Order.query.filter_by(user_id=user_id, id=id).first_or_404()
    return jsonify(order.to_dict())


@bp.route('/order/finish/client', methods=['POST'])
@jwt_required()
def order_finish_client():
    user_id = get_jwt_identity()

    data: dict = request.get_json()
    order_id = data["order_id"]
    order: OrderType = Order.query.filter_by(user_id=user_id, id=order_id).first_or_404()
    delivery = data.get("delivery", order.delivery)
    delivery_to = data["delivery_to"]
    if not delivery_to:
        return jsonify({'message': 'err'}), 404
    order.delivery = delivery
    order.delivery_to = delivery_to
    order.status = "Wait for send delivery"
    arr_supplier_id = []
    for id, item in enumerate(order.cart_group.cart_items):
        order.cart_group.cart_items[id].status = "Wait for send delivery"
        if item.product.user_id not in arr_supplier_id:
            notification = Notification(supplier_id=item.product.user_id, order_id=order.id)
            db.session.add(notification)
            arr_supplier_id.append(item.product.user_id)
    db.session.commit()
    return jsonify({'message': 'Finish order'})


@bp.route('/order/finish/supplier', methods=['POST'])
@jwt_required()
def order_finish_supplier():
    user_id = get_jwt_identity()

    data: dict = request.get_json()
    order_id = data["order_id"]
    order: OrderType = Order.query.filter_by(id=order_id).first_or_404()

    for id, item in enumerate(order.cart_group.cart_items):
        if item.product.user_id == user_id:
            order.cart_group.cart_items[id].status = "Sent"
    found_not_sent = False
    for item in order.cart_group.cart_items:
        if item.status != "Sent" and item.status != "Made":
            found_not_sent = True
            break
    if not found_not_sent:
        order.status = "All sent"

    db.session.commit()
    return jsonify({'message': 'Finish order'})


@bp.route('/order/confirm', methods=['POST'])
@jwt_required()
def order_confirm():
    user_id = get_jwt_identity()

    data: dict = request.get_json()
    order_id = data["order_id"]
    item_id = data.get("item_id")
    order: OrderType = Order.query.filter_by(user_id=user_id, id=order_id).first_or_404()

    if item_id:
        item: CartItemType = CartItem.query.filter_by(id=item_id).first_or_404()
        item.status = "Made"
        found_not_made = False
        for item in order.cart_group.cart_items:
            if item.status != "Made":
                found_not_made = True
                break
        if not found_not_made:
            order.status = "All made"
    else:
        for id, item in enumerate(order.cart_group.cart_items):
            order.cart_group.cart_items[id].status = "Made"
        order.status = "All made"

    db.session.commit()
    return jsonify({'message': 'Confirm order'})
