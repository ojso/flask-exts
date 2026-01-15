import pytest
from flask import Flask
from flask_exts.datastore.sqla import db


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY="test_key",
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    # app.config["SQLALCHEMY_ECHO"] = True
    db.init_app(app)
    return app


@pytest.fixture
def client(app):
    return app.test_client()



