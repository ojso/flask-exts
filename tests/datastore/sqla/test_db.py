import pytest
# from flask_exts.datastore.sqla.db import Db
from flask_exts.datastore.sqla import db
from sqlalchemy.orm import Session

class TestDb:

    def test_session(self,app):
        with pytest.raises(RuntimeError):
            db.session()

        with app.app_context():
            first = db.session()
            assert isinstance(first, Session)
            second = db.session()
            assert first is second
            
        with app.app_context():
            third = db.session()
            assert first is not third