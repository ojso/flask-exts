import pytest
from flask import Flask
from flask_exts import Exts

from flask_exts.template.base import Template



@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "1"
    exts = Exts()
    exts.init_app(app)
    yield app
