import pytest
from flask import Flask
from flask_exts import Manager
from flask_exts.templating.theme import DefaultTheme
from flask_sqlalchemy import SQLAlchemy

bootstrap5_theme = DefaultTheme(bootstrap_version=5)

@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "1"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"
    app.config["TEMPLATE_THEME"] = bootstrap5_theme
    manager = Manager()
    manager.init_app(app)
    db = SQLAlchemy()
    db.init_app(app)
    yield app
