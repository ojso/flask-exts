import pytest
from flask import Flask
from flask_exts import Manager
from flask_exts.template.theme import BootstrapTheme

class MyManager(Manager):
    def get_theme(self):
        return BootstrapTheme(5)


@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "1"
    manager = MyManager()
    manager.init_app(app)
    yield app
