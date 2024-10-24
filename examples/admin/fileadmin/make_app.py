from flask import Flask
from flask_exts import Manager
from .admin_app import admin


def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    init_app(app)
    return app


def init_app(app: Flask):
    manager = Manager()
    manager.init_app(app)

    # Flask views
    @app.route("/")
    def index():
        return '<a href="/admin/">Click me to get to Admin!</a>'

    admin.init_app(app)
