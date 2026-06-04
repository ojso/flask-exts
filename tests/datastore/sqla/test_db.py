import pytest
from flask import Flask
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.orm import scoped_session, sessionmaker

from flask_exts.datastore.sqla.db import Db


def test_init_session_sets_engine_and_sessionmaker():
    db = Db()
    db.init_session(url="sqlite:///:memory:")

    assert db.engine is not None
    assert isinstance(db.session, sessionmaker)

    session = db.session()
    assert session.bind is db.engine
    session.close()


def test_init_app_registers_extension_and_adds_models_to_shell():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    db = Db()
    db.init_app(app)

    assert app.extensions["sqlalchemy"] is db
    assert isinstance(db.session, scoped_session)

    with app.app_context():
        class User(db.Model):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))

        db.create_all()
        db.add(User(name="alice"))
        db.commit()

        result = db.session.execute(select(User)).scalars().first()
        assert result is not None
        assert result.name == "alice"

        shell_context = db._add_models_to_shell()
        assert shell_context["db"] is db
        assert shell_context["User"] is User


def test_reset_all_drops_and_recreates_tables():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    db = Db()
    db.init_app(app)

    with app.app_context():
        class Widget(db.Model):
            __tablename__ = "widgets"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))

        db.create_all()
        db.add(Widget(name="widget-1"))
        db.commit()

        result = db.session.execute(select(Widget)).scalars().all()
        assert len(result) == 1

        db.reset_all()
        db.session.remove()

        result = db.session.execute(select(Widget)).scalars().all()
        assert len(result) == 0


def test_getattr_raises_when_session_is_not_initialized():
    db = Db()
    with pytest.raises(AttributeError):
        _ = db.execute("SELECT 1")
