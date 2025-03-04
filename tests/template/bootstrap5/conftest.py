import pytest
from flask import Flask
from flask_exts import Manager
from flask_exts.template.theme import BootstrapTheme


@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "1"
    app.config["TEMPLATE_THEME"] = BootstrapTheme(5)
    manager = Manager()
    manager.init_app(app)
    yield app
