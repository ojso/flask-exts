import pytest
from flask import current_app
from sqlalchemy.orm import Session
from . import db



class TestDb:
    def test_init_db(self):
        assert getattr(db, "Model", None) is not None
        assert getattr(db, "engine", None) is None
        assert getattr(db, "session", None) is None

    def test_session(self, app):
        assert getattr(db, "Model", None) is not None
        assert getattr(db, "engine", None) is not None
        assert getattr(db, "session", None) is not None

        with pytest.raises(RuntimeError):
            db.session()

        with app.app_context():
            assert db is current_app.extensions["sqlalchemy"]
            first = db.session()
            assert isinstance(first, Session)
            second = db.session()
            assert first is second

        with app.app_context():
            third = db.session()
            assert first is not third
