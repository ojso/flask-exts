import pytest
from flask_sqlalchemy import SQLAlchemy

@pytest.fixture
def db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
    # app.config['SQLALCHEMY_ECHO'] = True
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)
    yield db

@pytest.fixture
def postgres_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/flask_test'
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db = SQLAlchemy(app)
    yield db

