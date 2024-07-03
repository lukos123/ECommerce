from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.extension import SQLAlchemy as SQLA
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config

db: SQLA = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.users import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/users')

    from app.products import bp as products_bp
    app.register_blueprint(products_bp, url_prefix='/products')

    from app.cart import bp as cart_bp
    app.register_blueprint(cart_bp, url_prefix='/cart')

    from app.notification import bp as notification_bp
    app.register_blueprint(notification_bp, url_prefix='/notification')

    return app
