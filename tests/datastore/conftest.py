import pytest
from flask import Flask
from flask_exts.datastore.sqla import db


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_ECHO"] = True
    db.init_app(app)
    return app
