import pytest
from flask import Flask
from flask_exts import Manager
from flask_sqlalchemy import SQLAlchemy


@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "1"
    app.config["TEMPLATE_NAME"] = "bootstrap"
    app.config["BOOTSTRAP_VERSION"] = 4
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"
    manager = Manager()
    manager.init_app(app)
    db = SQLAlchemy()
    db.init_app(app)
    yield app
