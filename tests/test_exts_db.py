import pytest
from sqlalchemy import select
from flask_exts.datastore.sqla import db
from .models.simple import SimpleModel


def test_db(app):
    assert "sqlalchemy" in app.extensions
    assert app.extensions["sqlalchemy"] is db

    with app.app_context():
        db.create_all()
        simple_model = SimpleModel(name="test")
        db.session.add(simple_model)
        db.session.commit()
        
        retrieved_model = db.session.execute(select(SimpleModel)).scalars().first()
        # print(f"Retrieved model name: {retrieved_model.name}")
        assert retrieved_model is not None
        assert retrieved_model.name == "test"
