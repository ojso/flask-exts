import pytest
from flask import Flask
from flask_exts import Manager
from flask_exts.templating.theme import DefaultTheme

bootstrap5_theme = DefaultTheme(bootstrap_version=5)

@pytest.fixture
def app(db):
    app = Flask(__name__)
    app.secret_key = "1"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"
    app.config["TEMPLATE_THEME"] = bootstrap5_theme
    manager = Manager()
    manager.init_app(app)
    db.init_app(app)
    yield app
