from flask import Flask
from flask import current_app
from flask import g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Db:
    def __init__(self, app: Flask | None = None):
        self.Model = self._make_declarative_base()
        if app is not None:
            self.init_app(app)

    def _make_declarative_base(self):
        return Base

    def init_app(self, app: Flask) -> None:
        if "sqlalchemy" in app.extensions:
            raise RuntimeError("A 'SQLAlchemy' instance has already been registered.")
        app.extensions["sqlalchemy"] = self

        # engine
        engine_options = {
            "url": app.config.get("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")
        }
        if app.config.get("SQLALCHEMY_ECHO"):
            engine_options["echo"] = True
        self.engine = self._make_engine(engine_options)

        # session
        session_options = {"bind": self.engine}
        self.session = self._make_scoped_session(session_options)
        app.teardown_appcontext(self._remove_session)

        # cli
        app.shell_context_processor(self._add_models_to_shell)

    def _make_engine(self, options: dict):
        return create_engine(**options)

    def _make_scoped_session(self, options):
        session_factory = sessionmaker(**options)
        return scoped_session(session_factory, scopefunc=self._get_app_g_id)

    def _get_app_g_id(self) -> int:
        return id(g._get_current_object())

    def _remove_session(self, exception=None):
        """Remove the current session at the end of the request."""
        self.session.remove()

    def _add_models_to_shell(self):
        """Registered with :meth:`~flask.Flask.shell_context_processor`.
        Adds the ``db`` instance and all model classes to ``flask shell``.
        """
        db = current_app.extensions["sqlalchemy"]
        out = {m.class_.__name__: m.class_ for m in db.Model.registry.mappers}
        out["db"] = db
        return out

    def create_all(self,**kwargs):
        if 'bind' not in kwargs:
            kwargs['bind'] = self.engine
        self.Model.metadata.create_all(**kwargs)

    def reset_models(self):
        self.Model.metadata.drop_all(self.engine)
        self.Model.metadata.create_all(self.engine)
