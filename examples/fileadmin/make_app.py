from flask import Flask
from flask_exts import Manager
from .file_view import file_view
from flask_exts.datastore.sqla import db


def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["ADMIN_ACCESS_ENABLED"] = False
    init_app(app)
    return app


def init_app(app: Flask):
    manager = Manager()
    manager.init_app(app)

    with app.app_context():
        # db.drop_all()
        db.create_all()

    admin = manager.admins[0]
    admin.add_view(file_view)
