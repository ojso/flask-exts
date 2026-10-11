from flask import Flask, g
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool

#: Key under which this instance is stored in ``app.extensions``.
#: Deliberately *not* "sqlalchemy" -- that key belongs to Flask-SQLAlchemy,
#: and reusing it would make the two extensions mutually exclusive in the
#: same app.
_EXTENSION_KEY = "flask_exts_sqla"


class SqlaDb:
    """sqlalchemy db

    Example:
        Create a db::

            db = SqlaDb()
            db.init_app(app)
    """

    def __init__(self, app: Flask | None = None):
        self.Model = self._make_declarative_base()
        self.engine: Engine | None = None
        self.session: scoped_session | None = None
        # The app this instance is currently bound to, or None if unbound.
        # Guards against silently rebinding a live instance to a second,
        # different Flask app (see init_app()). dispose() clears this back
        # to None, which is what makes it safe to reuse the same SqlaDb()
        # across short-lived apps in a test suite: each test's fixture
        # calls dispose() before the next one calls init_app() again.
        self.app: Flask | None = None
        if app is not None:
            self.init_app(app)

    def _make_declarative_base(self) -> type[DeclarativeBase]:
        class Base(DeclarativeBase):
            pass

        return Base

    def init_app(self, app: Flask) -> None:
        if self.app is not None:
            # Rebinding this singleton to a (possibly different) app would
            # silently swap out engine/session for every other reference to
            # it: model modules, other extensions, request handlers already
            # running against the previously-bound app. Refuse outright --
            # call dispose() first if the intent really is to reuse this
            # instance for a new app (e.g. between test runs).
            raise RuntimeError(
                "This SqlaDb instance is already bound to an application "
                f"({self.app!r}). Call dispose() first if you intend to "
                "rebind it to a different app (e.g. between test runs), "
                "or create a separate SqlaDb() instance per application."
            )

        if _EXTENSION_KEY in app.extensions:
            raise RuntimeError(
                "A 'SqlaDb' instance has already been registered on this app."
            )

        database_uri = app.config.get("SQLALCHEMY_DATABASE_URI")
        if not database_uri:
            raise RuntimeError(
                "SQLALCHEMY_DATABASE_URI is not set. Configure it before "
                "calling init_app(), e.g. "
                'app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"'
            )

        # Only commit to the new app once we know init_app() will succeed:
        # if we failed above (missing URI), a retry with a fixed config
        # must still see this instance as unbound.
        self.app = app
        app.extensions[_EXTENSION_KEY] = self

        engine_options = {"url": database_uri}
        if app.config.get("SQLALCHEMY_ECHO"):
            engine_options["echo"] = True

        # In-memory SQLite defaults to SingletonThreadPool, which hands each
        # thread its own connection -- and therefore its own, separately
        # empty, in-memory database. A request served on a different thread
        # than the one that created the schema would see no tables at all.
        # Pin it to a single shared connection instead, same as
        # Flask-SQLAlchemy does for this case.
        if database_uri.startswith("sqlite://") and (
            ":memory:" in database_uri or database_uri in ("sqlite://", "sqlite:///")
        ):
            engine_options.setdefault("poolclass", StaticPool)
            engine_options.setdefault("connect_args", {"check_same_thread": False})

        engine_opts = app.config.get("SQLALCHEMY_ENGINE_OPTIONS", {})
        engine_options.update(engine_opts)
        self.engine = self._make_engine(engine_options)

        session_options = {"bind": self.engine}
        session_options.update(app.config.get("SQLALCHEMY_SESSION_OPTIONS", {}))
        self.session = self._make_scoped_session(session_options)

        app.teardown_appcontext(self._teardown_session)
        app.shell_context_processor(self._add_models_to_shell)

    def _make_engine(self, options: dict) -> Engine:
        return create_engine(**options)

    def _make_scoped_session(self, options: dict) -> scoped_session:
        session_factory = sessionmaker(**options)
        return scoped_session(session_factory, scopefunc=self._get_scope_object)

    def _get_scope_object(self):
        # Keyed on the app context object itself (as Flask-SQLAlchemy does),
        # not id(g): an id can be recycled by the GC once a context object
        # is freed, which could in theory hand a stale session to an
        # unrelated later context sharing the same memory address.
        return g._get_current_object()

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

    def dispose(self):
        if self.session is not None:
            try:
                self.session.remove()
            except RuntimeError:
                # No active app context, so the scoped registry has no key
                # to address. There's nothing to remove in that case; still
                # fall through to dispose the engine's connection pool.
                pass
        if self.engine is not None:
            self.engine.dispose()
        # Mark this instance unbound again so init_app() can be safely
        # called with a different app afterwards (see init_app()'s guard).
        self.app = None
