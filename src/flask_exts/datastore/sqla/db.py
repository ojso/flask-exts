from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from flask import Flask
from flask import g


class Db:
    """sqlalchemy database

    Examples:
        db = Db(app)
        db.init_app(app)
    """

    def __init__(self, app: Flask | None = None):
        self.Model = self._make_declarative_base()
        self.engine: Engine | None = None
        self.session: scoped_session | None = None
        if app is not None:
            self.init_app(app)

    def _make_declarative_base(self) -> type[DeclarativeBase]:
        class Base(DeclarativeBase):
            pass

        return Base

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

        app.teardown_appcontext(self._teardown_session)
        app.shell_context_processor(self._add_models_to_shell)

    def _make_engine(self, options: dict) -> Engine:
        return create_engine(**options)

    def _make_scoped_session(self, options: dict) -> scoped_session:
        session_factory = sessionmaker(**options)
        return scoped_session(session_factory, scopefunc=self._get_scope_id)

    def _get_scope_id(self) -> int:
        return id(g._get_current_object())

    def _teardown_session(self, exception: Exception | None = None) -> None:
        self.session.remove()

    def _add_models_to_shell(self) -> dict:
        out = {m.class_.__name__: m.class_ for m in self.Model.registry.mappers}
        out["db"] = self
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
