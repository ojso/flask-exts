import pytest
from flask import Flask
from flask_exts import Manager


@pytest.fixture
def app():
    app = Flask(__name__)
    # app.secret_key = "test_key"
    # app.debug = True
    app.config.update(
        TESTING=True,
        SECRET_KEY="test_key",
    )
    app.config["BABEL_ACCEPT_LANGUAGES"] = "en;zh;fr;de;ru"
    app.config["BABEL_DEFAULT_TIMEZONE"] = "Asia/Shanghai"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    # app.config["SQLALCHEMY_ECHO"] = True
    app.config["JWT_SECRET_KEY"] = "SECRET_KEY"
    app.config["JWT_HASH"] = "HS256"
    app.config.from_pyfile('config_prod.py', silent=True)
    manager = Manager()
    manager.init_app(app)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def manager(app):
    if hasattr(app, "extensions") and "manager" in app.extensions:
        return app.extensions["manager"]
    else:
        return None


@pytest.fixture
def admin(manager):
    return manager.admin

@pytest.fixture
def email(manager):
    return manager.email
