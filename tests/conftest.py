import pytest
from flask import Flask
from flask_exts import Manager


@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "1"
    app.config["BABEL_ACCEPT_LANGUAGES"] = "en;zh;fr;de;ru"
    app.config["BABEL_DEFAULT_TIMEZONE"] = "Asia/Shanghai"
    manager = Manager()
    manager.init_app(app)
    yield app


@pytest.fixture
def client(app):
    return app.test_client()
