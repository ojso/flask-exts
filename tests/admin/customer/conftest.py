import pytest
from flask import Flask
from flask_exts import Exts


@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "1"
    app.config["BABEL_ACCEPT_LANGUAGES"] = "en;zh;fr;de;ru"
    app.config["BABEL_DEFAULT_TIMEZONE"] = "Asia/Shanghai"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    # app.config["SQLALCHEMY_ECHO"] = True
    app.config["JWT_SECRET_KEY"] = "SECRET_KEY"
    app.config["JWT_HASH"] = "HS256"
    app.config["ADMIN_ALL_ACCESSED"] = False
    exts = Exts()
    exts.init_app(app)
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def exts(app):
    if hasattr(app, "extensions") and "exts" in app.extensions:
        return app.extensions["exts"]
    else:
        return None


@pytest.fixture
def admin(exts):
    return exts.admin
