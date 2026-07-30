import pytest
from flask import Flask
from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import scoped_session
from flask_exts.datastore.sqla.db import Db


def test_scoped_session():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    db = Db()
    db.init_app(app)

    with pytest.raises(RuntimeError):
        db.session()

    with app.app_context():
        session1 = db.session()
        session2 = db.session()
        assert session1 is session2

    with app.app_context():
        session3 = db.session()
        assert session1 is not session3


def test_init_app_registers_extension_and_adds_models_to_shell():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    db = Db()

    class Demo(db.Model):
        __tablename__ = "demo"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(50))

    db.init_app(app)

    assert app.extensions["sqlalchemy"] is db
    assert isinstance(db.session, scoped_session)

    with app.app_context():
        db.create_all()
        db.session.add(Demo(name="demo1"))
        db.session.commit()

        result = db.session.execute(select(Demo)).scalars().first()
        assert result is not None
        assert result.name == "demo1"

        shell_context = db._add_models_to_shell()
        assert shell_context["db"] is db
        assert shell_context["Demo"] is Demo


def test_reset_all_drops_and_recreates_tables():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    db = Db()

    class Demo(db.Model):
        __tablename__ = "demo"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(50))

    db.init_app(app)

    with app.app_context():
        db.create_all()
        db.session.add(Demo(name="demo1"))
        db.session.commit()

        result = db.session.execute(select(Demo)).scalars().all()
        assert len(result) == 1

        db.reset_all()
        result = db.session.execute(select(Demo)).scalars().all()
        assert len(result) == 0
