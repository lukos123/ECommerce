
import pytest

from app import create_app, db
from app.models import User, Product, CartItem, UserType, ProductType, Comment, CommentType, CartItemType, \
    CartItemGroupType, CartItemGroup, Order, OrderType
from config import ConfigTest


@pytest.fixture
def client():
    app = create_app(ConfigTest)
    client = app.test_client()

    with app.app_context():
        db.create_all()
        yield client
        db.drop_all()


def test_create_user(client):
    response = client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['access_token']
    assert data['refresh_token']
    user: User = User.query.filter_by(username="testuser").first()
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "testuser@example.com"
    assert user.check_password("testpassword")
    response = client.post('/auth/register', json={
        'username': 'te',
        'email': 'testuser2@example.com',
        'password': 'testpassword'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data["message"] == "Name is short"

    response = client.post('/auth/register', json={
        'username': 'testuser2',
        'email': 'testuserexample.com',
        'password': 'testpassword'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data["message"] == "Email is not valid"


def test_login_user(client):
    test_create_user(client)
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['access_token']
    assert data['refresh_token']


def test_product(client):
    response = client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    })
    assert response.status_code == 201
    access_token = response.get_json()["access_token"]
    user: UserType = User.query.filter_by(username="testuser").first()

    response = client.post('/products/', json={
        'name': 'name',
        'price': 100,
        'description': 'testdescription',

    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token
    })
    assert response.status_code == 201
    response = client.post('/products/', json={
        'name': 'name2',
        'price': 1002,
        'description': 'testdescription2'
    })
    assert response.status_code == 401
    response = client.get('/products')
    data = response.get_json()
    assert data[0]["name"] == "name"
    assert data[0]["price"] == 100
    assert data[0]["description"] == "testdescription"
    assert len(user.products) == 1
    assert user.products[0].name == "name"
    assert user.products[0].price == 100
    assert user.products[0].description == "testdescription"
    product: ProductType = Product.query.filter_by(description="testdescription").first()
    assert product is not None
    assert product.user.username == "testuser"
    response = client.put(f'/products/{product.id}', json={
        'name': 'name2',
        'price': 1002,
        'description': 'testdescription2',
    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token
    })
    data = response.get_json()
    assert response.status_code != 404
    assert data["name"] == "name2"
    assert data["price"] == 1002
    assert data["description"] == "testdescription2"
    assert product.name == "name2"
    assert product.price == 1002
    assert product.description == "testdescription2"
    response = client.put(f'/products/{product.id + 1}', json={
        'name': 'name2',
        'price': 1002,
        'description': 'testdescription2',
    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token
    })
    assert response.status_code == 404
    response = client.get(f'/products/{product.id}')
    assert response.status_code != 404
    data = response.get_json()
    assert data["name"] == product.name
    assert data["price"] == product.price
    assert data["description"] == product.description

    response = client.post(f'/products/{product.id}/comments', json={
        "text": "testtext"
    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token
    })
    data = response.get_json()
    assert data["text"] == "testtext"
    assert data["user"] == "testuser"
    comment: CommentType = Comment.query.filter_by(id=data["id"]).first()
    assert comment is not None
    assert comment.user.username == "testuser"
    assert comment.text == "testtext"
    response = client.get(f'/products/{product.id}/comments')
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["text"] == "testtext"
    assert data[0]["user"] == "testuser"

    response = client.delete(f'/products/{product.id}', headers={

        "Authorization": 'Bearer ' + access_token
    })
    assert response.status_code != 404
    data = response.get_json()
    assert data["message"] == "Product deleted"
    response = client.delete(f'/products/{product.id}', headers={

        "Authorization": 'Bearer ' + access_token
    })
    assert response.status_code == 404

    response = client.get(f'/products/{product.id}')
    assert response.status_code == 404


def test_cart(client):
    response = client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    })
    assert response.status_code == 201
    access_token = response.get_json()["access_token"]
    user: UserType = User.query.filter_by(username="testuser").first()
    data = client.post('/products/', json={
        'name': 'name',
        'price': 100,
        'description': 'testdescription',
    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token
    }).get_json()
    id_product = data["id"]
    assert id_product == 1
    cart_item_main_group: CartItemGroupType = CartItemGroup.query.first()
    assert cart_item_main_group.order is None
    response = client.post("/cart/", json={
        "product_id": id_product,
        "quantity": 1,
    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token
    })
    data = response.get_json()
    assert response.status_code == 201
    assert data["name"] == "name"
    assert data["quantity"] == 1
    cart: CartItemType = CartItem.query.filter_by(id=data["id"]).first()
    assert cart is not None
    assert cart.product.name == "name"
    assert cart.quantity == 1

    response = client.post("/cart", json={
        "product_id": id_product,
        "quantity": 1,
    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token
    })
    data = response.get_json()
    assert response.status_code == 201
    assert data["name"] == "name"
    assert data["quantity"] == 2
    cart: CartItemType = CartItem.query.filter_by(id=data["id"]).first()
    assert cart is not None
    assert cart.product.name == "name"
    assert cart.quantity == 2

    response = client.post("/cart/", json={
        "product_id": id_product,
        "quantity": 2,
    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token
    })
    data = response.get_json()
    assert response.status_code == 201
    assert data["name"] == "name"
    assert data["quantity"] == 4
    assert cart.product.name == "name"
    assert cart.quantity == 4
    response = client.get("/cart/main",  headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token
    })
    data = response.get_json()
    assert len(data["cart_items"]) == 1
    response = client.put(f"/cart/{cart.id}", json={
        "quantity": 10
    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token
    })
    data = response.get_json()
    assert data["name"] == "name"
    assert data["quantity"] == 10
    assert cart.product.name == "name"
    assert cart.quantity == 10
    response = client.delete(f"/cart/{cart.id}", headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token
    })
    data = response.get_json()
    assert data["message"] == "Cart item deleted"
    cart: CartItemType = CartItem.query.filter_by(id=cart.id).first()

    assert cart is None


def test_cart_order(client):
    response = client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    })
    assert response.status_code == 201
    access_token = response.get_json()["access_token"]

    response = client.post('/auth/register', json={
        'username': 'testuser2',
        'email': 'testuser2@example.com',
        'password': 'testpassword2'
    })
    assert response.status_code == 201
    access_token2 = response.get_json()["access_token"]

    response = client.post('/products/', json={
        'name': 'name',
        'price': 100,
        'description': 'testdescription',

    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token2
    })
    assert response.status_code == 201

    product: ProductType = Product.query.filter_by(name="name").first()
    response = client.post('/products/', json={
        'name': 'name2',
        'price': 100,
        'description': 'testdescription',

    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token2
    })
    assert response.status_code == 201

    product: ProductType = Product.query.filter_by(name="name").first()
    assert product.id
    response = client.post("/cart/", json={
        "product_id": product.id,
        "quantity": 2,
    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token
    })
    assert response.status_code == 201

    product: ProductType = Product.query.filter_by(name="name2").first()
    assert product.id
    response = client.post("/cart/", json={
        "product_id": product.id,
        "quantity": 1,
    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token
    })
    assert response.status_code == 201

    response = client.post('/cart/order', headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token
    })
    assert response.status_code != 401
    assert response.get_json()["message"] == "Start order"
    order: OrderType = Order.query.first()
    cart_item_group: CartItemGroupType = CartItemGroup.query.filter(CartItemGroup.user_id == order.user_id, CartItemGroup.order !=None).first()
    cart_item_main_group: CartItemGroupType = CartItemGroup.query.filter(CartItemGroup.user_id == order.user_id, CartItemGroup.order ==None).first()

    assert order.cart_item_group_id == cart_item_group.id
    assert cart_item_group.order is not None
    assert cart_item_main_group.order is None

    assert len(order.cart_group.cart_items) == 2
    response = client.get('/cart/order/all', headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token
    })
    assert response.status_code !=404
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["id"] == 1

    response = client.get('/cart/order/1', headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token
    })
    assert response.status_code != 404
    data = response.get_json()
    assert data["id"] == 1

    response = client.post('/cart/order/finish/client', json={
        "order_id": order.id,
        "delivery": "delivery1",
        "delivery_to": "muhosr 20",
    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token
    })
    assert response.status_code != 404
    assert order.status == "Wait for send delivery"
    assert response.get_json()["message"] == "Finish order"

    response = client.get('/notification', json={

    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token2
    })

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1

    response = client.get('/notification/not_made', json={

    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token2
    })

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1

    response = client.get('/notification/not_sent', json={

    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token2
    })

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1

    user_1: UserType = User.query.filter_by(email="testuser2@example.com").first()
    user: UserType = User.query.filter_by(email="testuser@example.com").first()
    assert len(user_1.notifications) == 1
    assert user_1.notifications[0].order.delivery_to == "muhosr 20"
    assert user_1.notifications[0].order.delivery == "delivery1"
    assert len(user.notifications) == 0
    assert len(user.orders) == 1

    response = client.post('/cart/order/finish/supplier', json={
        "order_id": order.id

    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token2
    })
    assert response.status_code != 404
    assert response.get_json()["message"] == "Finish order"
    assert len(order.cart_group.cart_items) == 2
    assert order.cart_group.cart_items[0].status == "Sent"
    assert order.cart_group.cart_items[1].status == "Sent"
    assert order.status == "All sent"

    response = client.get('/notification/sent', json={

    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token2
    })

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1

    response = client.post('/cart/order/confirm', json={
        "order_id": order.id

    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token
    })
    assert response.status_code != 404
    assert response.get_json()["message"] == "Confirm order"
    assert order.cart_group.cart_items[0].status == "Made"
    assert order.cart_group.cart_items[1].status == "Made"
    assert order.status == "All made"

    response = client.get('/notification/sent', json={

    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token2
    })

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 0

    response = client.get('/notification/made', json={

    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token2
    })

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1


def test_user(client):
    response = client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    })
    assert response.status_code == 201
    access_token = response.get_json()["access_token"]
    response = client.get('/users/main', json={
    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token
    })
    assert response.status_code < 300
    data = response.get_json()

    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert len(data["products"]) == 0
    assert len(data["comments"]) == 0
    assert len(data["orders"]) == 0
    assert len(data["cart_item_groups"]) == 1

    response = client.put('/users/main', json={
        "username": "testuser2",
        "email": "email3@gmail.com",
        "password": "dog123",
        "description": "dog22222"
    }, headers={
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + access_token
    })
    assert response.status_code < 300
    data = response.get_json()
    assert data["username"] == "testuser2"
    assert data["email"] == "email3@gmail.com"
    user: UserType = User.query.filter_by(username="testuser2").first()
    assert user.check_password("dog123")
    assert data["description"] == 'dog22222'



# def tesdata = response.get_json()t_get_user(client):
#     user = User(username='testuser', email='testuser@example.com')
#     user.set_password('testpassword')
#     db.session.add(user)
#     db.session.commit()
#
#     response = client.get(f'/api/users/{user.id}')
#     assert response.status_code == 200
#     data = response.get_json()
#     assert data['username'] == 'testuser'
