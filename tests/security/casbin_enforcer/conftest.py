import pytest
import os
from flask import Flask


@pytest.fixture
def app():
    app = Flask("test")
    app.testing = True
    app.config["CASBIN_MODEL"] = (
        os.path.split(os.path.realpath(__file__))[0] + "/casbin_files/rbac_model.conf"
    )
    # Set headers where owner for enforcement policy should be located
    app.config["CASBIN_OWNER_HEADER"] = "Authorization"
    app.config["JWT_SECRET_KEY"] = "SECRET_KEY"
    app.config["JWT_HASH"] = "HS256"

    yield app


@pytest.fixture
def client(app):
    return app.test_client()
