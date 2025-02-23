import os.path as op
from flask import Flask
from flask_exts import Manager
from .user_center import UserCenter


def get_sqlite_path():
    app_dir = op.realpath(op.dirname(__file__))
    database_path = op.join(app_dir, "sample.sqlite")
    return database_path


def register_users(app):
    user_center = app.config["USER_CENTER"]
    user_center.register_user("admin", "admin", "admin@example.com")


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"

    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    # app.config["SQLALCHEMY_ECHO"] = True
    app.config["DATABASE_FILE"] = get_sqlite_path()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + app.config["DATABASE_FILE"]

    app.config["USER_CENTER"] = UserCenter()

    init_app(app)

    return app


def init_app(app: Flask):

    manager = Manager()
    manager.init_app(app)

    from .models import init_models
    
    init_models()

    from .admin_views import add_views

    add_views(app)

    if not op.exists(app.config["DATABASE_FILE"]):
        with app.app_context():
            from .build_sample import build_sample_db

            build_sample_db()
            register_users(app)
