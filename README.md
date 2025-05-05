# ECommerce API

A RESTful API for a simple e-commerce platform built with Flask, inspired by anime store dreams ✨

## Features

* **User Authentication**: Register, log in, and refresh tokens via JWT.
* **User Profiles**: View and update your profile, including uploading a cute avatar.
* **Product Management**: Create, read, update, and delete products; upload product images.
* **Shopping Cart**: Add items, update quantities, and view your main cart.
* **Order Processing**: Start orders, finish as client or supplier, and confirm delivery.
* **Notifications**: Suppliers get notified of new orders and order updates.

## Tech Stack

* **Python 3.x**
* **Flask**
* **Flask-SQLAlchemy**
* **Flask-Migrate**
* **Flask-JWT-Extended**
* **Flask-CORS**
* **MySQL** (production) / **SQLite** (testing)
* **pytest** for testing

## Setup & Installation

1. **Clone the repo**:

   ```bash
   git clone <your-repo-url>
   cd <your-repo-folder>
   ```

2. **Create a virtual environment & install dependencies**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables** (optional, defaults provided in `config.py`):

   * `SECRET_KEY`: secret for Flask sessions
   * `DATABASE_URL`: SQLAlchemy DB URI (default uses MySQL)
   * `JWT_SECRET_KEY`: secret for JWT tokens

4. **Initialize the database**:

   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. **Run the application**:

   ```bash
   python run.py
   ```

   The API will be running at `http://localhost:5001/`.

## API Documentation

You can browse the interactive API docs at:

```
http://localhost:5001/documentation
```

## Endpoints Overview

### Auth

| Method | Endpoint         | Description           |
| ------ | ---------------- | --------------------- |
| POST   | `/auth/register` | Register a new user   |
| POST   | `/auth/login`    | Log in and get tokens |
| POST   | `/auth/refresh`  | Refresh access token  |

### Users

| Method | Endpoint      | Description                 |
| ------ | ------------- | --------------------------- |
| GET    | `/users`      | List all user profiles      |
| GET    | `/users/main` | Get authenticated user info |
| PUT    | `/users/main` | Update your profile         |
| GET    | `/users/<id>` | Get a user's public profile |

### Products

| Method | Endpoint                       | Description                 |
| ------ | ------------------------------ | --------------------------- |
| GET    | `/products`                    | List all products           |
| GET    | `/products/<id>`               | Get product details         |
| POST   | `/products`                    | Create a new product        |
| PUT    | `/products/<id>`               | Update a product            |
| DELETE | `/products/<id>`               | Delete a product            |
| GET    | `/products/<id>/comments`      | List comments for a product |
| POST   | `/products/<id>/comments`      | Add a comment to a product  |
| PUT    | `/products/image/<product_id>` | Upload/update product image |

### Cart

| Method | Endpoint                      | Description                             |
| ------ | ----------------------------- | --------------------------------------- |
| GET    | `/cart`                       | List all your carts                     |
| GET    | `/cart/main`                  | Get your main (active) cart             |
| POST   | `/cart` / `/cart/`            | Add item(s) to your main cart           |
| PUT    | `/cart/<id>`                  | Update item quantity                    |
| DELETE | `/cart/<id>`                  | Remove an item from cart                |
| POST   | `/cart/order`                 | Start a new order                       |
| GET    | `/cart/order/all`             | List your orders                        |
| GET    | `/cart/order/<id>`            | Get order details                       |
| POST   | `/cart/order/finish/client`   | Finish order as a client (set delivery) |
| POST   | `/cart/order/finish/supplier` | Supplier marks items as sent            |
| POST   | `/cart/order/confirm`         | Client confirms receipt (make)          |

### Notifications

| Method | Endpoint                 | Description                             |
| ------ | ------------------------ | --------------------------------------- |
| GET    | `/notification`          | Get all your notifications              |
| GET    | `/notification/made`     | Notifications where order is made       |
| GET    | `/notification/not_made` | Notifications waiting for shipment/made |
| GET    | `/notification/sent`     | Notifications where items are all sent  |
| GET    | `/notification/not_sent` | Notifications waiting for shipment      |

## Running Tests

Make sure your virtual environment is active:

```bash
pytest
```

## Contributing

Feel free to file issues or send pull requests! Let’s make this project kawaii and powerful together 💖
