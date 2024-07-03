from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models import Product, ProductType, Comment

bp = Blueprint('products', __name__)


@bp.route('', methods=['GET'])
@bp.route('/', methods=['GET'])
def get_products():
    products: list[ProductType] = Product.query.all()
    return jsonify([product.to_dict() for product in products])


@bp.route('/<int:id>', methods=['GET'])
def get_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({}), 404
    return jsonify(product.to_dict())


# TODO
@bp.route('/<int:id>/comments', methods=['GET'])
def get_comments(id):
    product: ProductType = db.session.get(Product, id)
    if not product:
        return jsonify({}), 404
    return jsonify([comment.to_dict() for comment in product.comments])


@bp.route('/<int:id>/comments', methods=['POST'])
@jwt_required()
def add_comment(id):
    user_id = get_jwt_identity()
    data = request.get_json()
    if len(data.get("text", "")) > 0:
        comment = Comment(
            product_id=id,
            user_id=user_id,
            text=data["text"]
        )
        db.session.add(comment)
        db.session.commit()

        return jsonify(comment.to_dict())
    else:
        return jsonify({}), 404


@bp.route('/', methods=['POST'])
@bp.route('', methods=['POST'])
@jwt_required()
def add_product():
    user_id = get_jwt_identity()
    data = request.get_json()
    product = Product(
        name=data['name'],
        price=data['price'],
        user_id=user_id,
        description=data.get('description', '')
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201


@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_product(id):
    user_id = get_jwt_identity()
    data: dict = request.get_json()
    product: ProductType = db.session.get(Product, id)
    if product and product.user_id == user_id:
        product.name = data.get('name', product.name)
        product.price = data.get('price', product.price)
        product.description = data.get('description', product.description)
        db.session.commit()
        return jsonify(product.to_dict())
    else:
        return jsonify({}), 404


@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    user_id = get_jwt_identity()
    product: ProductType = db.session.get(Product, id)
    if product and product.user_id == user_id:
        for comment in product.comments:
            db.session.delete(comment)
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted'})
    return jsonify({}), 404
