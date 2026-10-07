"""
A module-level singleton of :class:`~flask_exts.datastore.sqla.database.SqlaDb`.

``db`` is the single global entry point for defining models and managing database sessions.
It wraps SQLAlchemy and binds to a single Flask application context.
After initialization, it can be used to:

- Define models via ``db.Model``
- Access the session via ``db.session``
- Access the engine via ``db.engine``

Example:
    Define a model::

        from sqlalchemy.orm import mapped_column
        from flask_exts.datastore.sqla import db

        class User(db.Model):
            __tablename__ = "users"

            id: Mapped[int] = mapped_column(primary_key=True)
            username: Mapped[str | None] = mapped_column(unique=True)
            password: Mapped[str | None]

    Use the session::

        user = User(name="alice")
        db.session.add(user)
        db.session.commit()

.. warning::

   The ``db`` instance is bound to a **single** Flask application context.
   Do **not** reuse this global instance across multiple Flask applications.
   If you need to support multiple applications, create a separate
   :class:`~flask_exts.datastore.sqla.database.SqlaDb` instance for each one.

See Also:
    - :class:`~flask_exts.datastore.sqla.database.SqlaDb`
    - SQLAlchemy: https://docs.sqlalchemy.org/
"""

from .database import SqlaDb

db = SqlaDb()
