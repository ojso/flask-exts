import pytest
from flask import Flask
from flask_exts import Manager
from flask_sqlalchemy import SQLAlchemy

db_sql = SQLAlchemy()


@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "1"
    app.config["BABEL_ACCEPT_LANGUAGES"] = "en;zh;fr;de;ru"
    app.config["BABEL_DEFAULT_TIMEZONE"] = "Asia/Shanghai"
    app.config["TEMPLATE_NAME"] = "bootstrap"
    manager = Manager()
    manager.init_app(app)
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db():
    return db_sql
