import pytest
from flask import Flask

from flask_exts import ExtensionManager


@pytest.fixture
def app():
    app = Flask(__name__)
    # app.secret_key = "test_key"
    # app.debug = True
    app.config.update(
        TESTING=True,
        SECRET_KEY="test_key",
    )
    app.config["ADMIN_ALLOW_ACCESS"] = True
    app.config["BABEL_ACCEPT_LANGUAGES"] = "en;zh;fr;de;ru"
    app.config["BABEL_DEFAULT_TIMEZONE"] = "Asia/Shanghai"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    # app.config["SQLALCHEMY_ECHO"] = True
    app.config["CSRF_ENABLED"] = False
    app.config["JWT_SECRET_KEY"] = (
        "SHA256_SECRET_KEY_RECOMMENDED_32_BYTES"  #  The HMAC key is recommended length of 32 bytes for SHA256. See RFC 7518 Section 3.2.
    )
    app.config["JWT_HASH"] = "HS256"
    exts = ExtensionManager()
    exts.init_app(app)
    yield app
    with app.app_context():
        exts.shutdown()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def exts(app):
    return app.extensions["exts"]


@pytest.fixture
def admin(exts):
    return exts.get_extension("admin").get_admin()


@pytest.fixture
def email(exts):
    return exts.get_extension("emailer").get_emailer()
