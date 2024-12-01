import os.path
from flask import Flask
from flask import render_template
from flask_exts import Manager
from flask_exts.admin import Admin
from .models import db
from .user_center import UserCenter
from .views.index_view import myview


def get_sqlite_path():
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, "sample.sqlite")
    return database_path


def build_sample_db(app):
    import string
    import random

    # db.drop_all()
    db.create_all()
    user_center = app.config["USER_CENTER"]
    user_center.register_user("admin", "admin", "admin@example.com")


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"
    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["DATABASE_FILE"] = get_sqlite_path()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + app.config["DATABASE_FILE"]

    app.config["USER_CENTER"] = UserCenter()

    init_app(app)

    return app


def init_app(app: Flask):
    from .models import init_db

    init_db(app)

    manager = Manager()
    manager.init_app(app)

    admin = Admin(name="Demo")
    admin.init_app(app)
    admin.add_view(myview,is_menu=False)

    if not os.path.exists(app.config["DATABASE_FILE"]):
        with app.app_context():
            build_sample_db(app)

