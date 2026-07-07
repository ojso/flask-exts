from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from flask import Flask
from flask import current_app
from flask import g


class Db:
    """sqlalchemy database

    Examples:
    1. Flask:
        db = Db(app)

    2. Flask delay:
        db = Db()
        db.init_app(app)

    3. No Flask
        db = Db()
        db.init_session(url="sqlite:///mydb.sqlite")

    """

    def __init__(self, app: Flask | None = None):
        self.Model = self._make_declarative_base()
        self.engine: Engine | None = None
        self.session: scoped_session | sessionmaker | None = None
        self._session_factory: sessionmaker | None = None
        if app is not None:
            self.init_app(app)

    def _make_declarative_base(self) -> type[DeclarativeBase]:
        class Base(DeclarativeBase):
            pass

        return Base

    def init_session(
        self, url: str | None = None, echo: bool = False, **engine_options
    ) -> None:
        """Initialize the database engine and session factory in non-Flask environments.

        Examples:
            db = Db()
            db.init_session(url="sqlite:///mydb.sqlite", echo=True)
            db.create_all()

            with db.session() as session:
                session.add(obj)
                session.commit()
        """
        self._cleanup()

        options = {"url": url or "sqlite:///:memory:"}
        if echo:
            options["echo"] = True
        options.update(engine_options)

        self.engine = create_engine(**options)
        self._session_factory = sessionmaker(bind=self.engine)
        self.session = self._session_factory

    def init_app(self, app: Flask) -> None:
        if "sqlalchemy" in app.extensions:
            raise RuntimeError("A 'SQLAlchemy' instance has already been registered.")
        app.extensions["sqlalchemy"] = self

        engine_options = {
            "url": app.config.get("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")
        }
        if app.config.get("SQLALCHEMY_ECHO"):
            engine_options["echo"] = True

        engine_opts = app.config.get("SQLALCHEMY_ENGINE_OPTIONS", {})
        engine_options.update(engine_opts)

        self.engine = self._make_engine(engine_options)

        session_options = {"bind": self.engine}
        self.session = self._make_scoped_session(session_options)

        print("Teardown registered") 
        app.teardown_appcontext(self._teardown_session)
        app.shell_context_processor(self._add_models_to_shell)

    def _cleanup(self) -> None:
        """clear old connections and sessions"""
        if self.session is not None:
            if isinstance(self.session, scoped_session):
                self.session.remove()
            self.session = None

        if self.engine is not None:
            self.engine.dispose()
            self.engine = None

        self._session_factory = None

    def _make_engine(self, options: dict) -> Engine:
        return create_engine(**options)

    def _make_scoped_session(self, options: dict) -> scoped_session:
        session_factory = sessionmaker(**options)
        return scoped_session(session_factory, scopefunc=self._get_scope_id)

    def _get_scope_id(self) -> int:
        return id(g._get_current_object())

    def _teardown_session(self, exception: Exception | None = None) -> None:
        print("teardown_session")
        if isinstance(self.session, scoped_session):
            print("teardown_session")
            if exception is not None:
                try:
                    self.session.rollback()
                except Exception:
                    pass
            self.session.remove()
            self.session = None

    def _add_models_to_shell(self) -> dict:
        db_instance = current_app.extensions["sqlalchemy"]
        if db_instance is None:
            return {}

        out = {m.class_.__name__: m.class_ for m in db_instance.Model.registry.mappers}
        out["db"] = db_instance
        return out

    def create_all(self, **kwargs):
        if "bind" not in kwargs:
            kwargs["bind"] = self.engine
        self.Model.metadata.create_all(**kwargs)

    def drop_all(self, **kwargs):
        if "bind" not in kwargs:
            kwargs["bind"] = self.engine
        self.Model.metadata.drop_all(**kwargs)

    def reset_all(self):
        self.Model.metadata.drop_all(self.engine)
        self.Model.metadata.create_all(self.engine)

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        if isinstance(self.session, scoped_session):
            return getattr(self.session, name)
        elif isinstance(self.session, sessionmaker):
            return getattr(self.session, name)
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
