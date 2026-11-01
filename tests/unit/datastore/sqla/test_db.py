import pytest
from flask import Flask
from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column, scoped_session
from sqlalchemy.pool import StaticPool

from flask_exts.datastore.sqla.database import SqlaDb


def test_init_app_requires_database_uri():
    app = Flask(__name__)
    # SQLALCHEMY_DATABASE_URI deliberately left unset.

    db = SqlaDb()
    with pytest.raises(RuntimeError, match="SQLALCHEMY_DATABASE_URI"):
        db.init_app(app)


def test_init_app_uses_distinct_extension_key_from_flask_sqlalchemy():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    db = SqlaDb()
    db.init_app(app)

    assert "flask_exts_sqla" in app.extensions
    # The "sqlalchemy" key is Flask-SQLAlchemy's; this extension must not
    # take it, or the two become mutually exclusive in the same app.
    assert "sqlalchemy" not in app.extensions


def test_init_app_pins_in_memory_sqlite_to_a_shared_connection():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

    db = SqlaDb()
    db.init_app(app)

    assert isinstance(db.engine.pool, StaticPool)


def test_dispose_without_app_context_does_not_raise():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    db = SqlaDb()
    db.init_app(app)

    # No app_context() here: dispose() must tolerate being called from a
    # teardown/shutdown path where none is active.
    db.dispose()


def test_reinitializing_a_bound_instance_without_dispose_raises():
    app1 = Flask(__name__)
    app1.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app2 = Flask(__name__)
    app2.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    db = SqlaDb()
    db.init_app(app1)

    # Same app again, or a different one -- either way, calling init_app()
    # on an instance that's still bound must be refused rather than
    # silently swapping the engine/session out from under existing
    # references to this `db`.
    with pytest.raises(RuntimeError, match="already bound"):
        db.init_app(app1)
    with pytest.raises(RuntimeError, match="already bound"):
        db.init_app(app2)


def test_dispose_allows_rebinding_to_a_different_app():
    app1 = Flask(__name__)
    app1.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app2 = Flask(__name__)
    app2.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    # One SqlaDb() instance reused across two short-lived apps, with a
    # dispose() in between -- the pattern the test suite's `app` fixture
    # relies on.
    db = SqlaDb()
    db.init_app(app1)
    db.dispose()

    assert db.app is None

    db.init_app(app2)
    assert db.app is app2
    assert app2.extensions["flask_exts_sqla"] is db


def test_scoped_session():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    db = SqlaDb()
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

    db = SqlaDb()

    class Demo(db.Model):
        __tablename__ = "demo"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(50))

    db.init_app(app)

    assert app.extensions["flask_exts_sqla"] is db
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

        db.dispose()



def test_reset_all_drops_and_recreates_tables():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    db = SqlaDb()

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

        db.dispose()
