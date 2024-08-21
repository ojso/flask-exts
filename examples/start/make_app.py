from flask import Flask


def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    init_app(app)
    return app


def init_app(app: Flask):
    from .models import init_db
    init_db(app)
    # register blueprints
    from .register_blueprints import register_blueprints

    register_blueprints(app)
