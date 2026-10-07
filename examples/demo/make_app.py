import os.path as op

from flask import Flask

from flask_exts import ExtensionManager


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = "dev"
    app.config.from_pyfile("config.py", silent=True)
    app.config.from_pyfile("config_prod.py", silent=True)
    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    # app.config["SQLALCHEMY_ECHO"] = True
    app.config["DATABASE_FILE"] = op.join(
        op.realpath(op.dirname(__file__)), "demo.sqlite"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + app.config["DATABASE_FILE"]
    init_app(app)
    return app


def init_app(app: Flask):
    exts = ExtensionManager()
    exts.init_app(app)

    from . import models

    from .admin_views import register_views

    register_views(app)

    if not op.exists(app.config["DATABASE_FILE"]):
        with app.app_context():
            from .build_sample import build_sample_db

            build_sample_db()
