Database
========

This page documents the database helpers and SQLAlchemy integration used by Flask-Exts.

Overview
--------

Flask-Exts ships a small SQLAlchemy wrapper, :class:`~flask_exts.datastore.sqla.database.SqlaDb`,
instead of depending on Flask-SQLAlchemy. A ready-to-use singleton is
exposed as ``db``::

    from flask_exts.datastore.sqla import db

``db`` is created at import time but stays unbound (``db.engine`` and
``db.session`` are ``None``) until :meth:`~flask_exts.datastore.sqla.database.SqlaDb.init_app`
runs -- which happens automatically when the built-in ``database`` extension
initializes. This two-step lifecycle is what lets model modules do::

    from flask_exts.datastore.sqla import db

    class User(db.Model):
        __tablename__ = "users"
        ...

at import time, before any Flask application exists yet.

.. warning::

   ``db`` is a **single-application** singleton. Calling ``init_app()``
   while it is still bound to an application -- whether that's the same
   app again or a different one -- raises ``RuntimeError`` rather than
   silently swapping out ``db.engine``/``db.session``. Call
   :meth:`~flask_exts.datastore.sqla.database.SqlaDb.dispose` first if you
   genuinely intend to rebind this instance to a different app (this is
   how the test suite reuses one ``db`` across many short-lived apps,
   calling ``dispose()`` in each test's teardown). For a long-running
   process that serves more than one Flask application at once, create a
   separate ``SqlaDb()`` instance per application instead.

Configuration
-------------

.. list-table:: Database configuration options
   :header-rows: 1
   :widths: 28 72

   * - Name
     - Description
   * - ``SQLALCHEMY_DATABASE_URI``
     - **Required.** SQLAlchemy connection URL, e.g.
       ``"sqlite:///app.db"`` or ``"postgresql+psycopg://user:pass@host/db"``.
       ``init_app()`` raises ``RuntimeError`` if this is unset.
   * - ``SQLALCHEMY_ECHO``
     - Set to ``True`` to log every SQL statement. Default is ``False``.
   * - ``SQLALCHEMY_ENGINE_OPTIONS``
     - Dict of keyword arguments forwarded to SQLAlchemy's
       ``create_engine()``. Use this for ``pool_size``, ``pool_recycle``,
       ``pool_pre_ping``, etc. Takes precedence over the two options above
       when keys overlap.
   * - ``SQLALCHEMY_SESSION_OPTIONS``
     - Dict of keyword arguments forwarded to ``sessionmaker()``, e.g.
       ``{"expire_on_commit": False}``. Default is ``{}``.

In-memory SQLite
-----------------

When ``SQLALCHEMY_DATABASE_URI`` points at an in-memory SQLite database
(``"sqlite://"`` or any URI containing ``":memory:"``), ``init_app()``
automatically pins the engine to a single shared connection
(``poolclass=StaticPool``, ``connect_args={"check_same_thread": False}``).

This matters because SQLite's default pooling for in-memory databases hands
each thread its *own*, separately empty, in-memory database -- so without
this override, a request served on a different thread than the one that
created the schema would see no tables at all. This is the same workaround
Flask-SQLAlchemy applies for this case.

You can override the pool explicitly via ``SQLALCHEMY_ENGINE_OPTIONS`` if
you need different behavior.

Long-lived connections (MySQL/PostgreSQL)
------------------------------------------

Database servers often close idle connections after a timeout (MySQL's
``wait_timeout`` is a common culprit). If your process keeps a connection
pool open across requests, configure ``pool_pre_ping`` and/or
``pool_recycle`` to avoid "server has gone away"-style errors::

    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

Session scope
-------------

``db.session`` is a SQLAlchemy ``scoped_session`` keyed on the current Flask
application context, matching Flask-SQLAlchemy's behavior: accessing
``db.session`` inside a request (or any ``with app.app_context():`` block)
always returns the same session object for that context, and a fresh one
once the context ends. The session is removed automatically via
``teardown_appcontext``.

Shutdown
--------

:meth:`~flask_exts.datastore.sqla.database.SqlaDb.dispose` releases the
session registry and the engine's connection pool, and marks the instance
unbound again (``db.app`` becomes ``None``), allowing a subsequent
``init_app()`` call with a different app. It tolerates being called with
no active application context (e.g. from a shutdown hook that isn't
running inside a request), in which case it skips removing the session
registry entry (there's nothing addressable without a context) but still
disposes the engine.

API reference
--------------

.. automodule:: flask_exts.datastore.sqla._db

.. automodule:: flask_exts.datastore.sqla.database
   :members:
