import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mysql+mysqlconnector://flaskuser:yourpassword@localhost/flaskapp?charset=utf8mb4&collation=utf8mb4_general_ci'
    # os.environ.get('DATABASE_URL') or \
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://flaskuser:yourpassword@localhost/flaskapp?charset=utf8mb4&collation=utf8mb4_general_ci'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'super-secret'


class ConfigTest:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mysql+mysqlconnector://flaskuser:yourpassword@localhost/flaskapp?charset=utf8mb4&collation=utf8mb4_general_ci'
    # os.environ.get('DATABASE_URL') or \
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'super-secret'
