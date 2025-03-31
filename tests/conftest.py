import pytest
from flask import Flask
from flask_exts import Manager


@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "1"
    app.config["BABEL_ACCEPT_LANGUAGES"] = "en;zh;fr;de;ru"
    app.config["BABEL_DEFAULT_TIMEZONE"] = "Asia/Shanghai"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    # app.config["SQLALCHEMY_ECHO"] = True
    app.config["JWT_SECRET_KEY"] = "SECRET_KEY"
    app.config["JWT_HASH"] = "HS256"
    manager = Manager()
    manager.init_app(app)
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin(app):
    if (
        hasattr(app, "extensions")
        and "admin" in app.extensions
        and len(app.extensions["admin"]) > 0
    ):
        return app.extensions["admin"][0]
    else:
        return None
