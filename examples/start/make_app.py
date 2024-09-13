from flask import Flask
from flask_exts import Manager

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TEMPLATE_NAME"] = "bootstrap"
    init_app(app)
    return app


def init_app(app: Flask):
    manager = Manager()
    manager.init_app(app)

    from .models import init_db
    init_db(app)
    # register blueprints
    from .register_blueprints import register_blueprints

    register_blueprints(app)


