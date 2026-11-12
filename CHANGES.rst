Changelog
=========

All notable changes to this project are documented in this file.

Unreleased
----------

Changed
~~~~~~~

- Rename ``RowsActionHandler`` to ``BulkActionHandler`` and move the handlers
  to ``row_actions.py`` / ``bulk_actions.py``.
- Measure coverage for ``src/flask_exts`` only.

Removed
~~~~~~~

- Remove the unused ``datastore/sqla/query_builders`` package.
- Remove the ``requires_active`` decorator; disabled accounts are rejected at
  login and their sessions are invalidated by ``user_loader``.
- Remove commented-out API-key and Basic Auth placeholders from the request
  loader; only Bearer JWT is supported.

Fixed
~~~~~

- Validate the registration email format and maximum length.
- Encode admin list URLs with ``urlencode`` and remove the dead
  ``hasattr`` branch in pagination.
- Align admin list totals with the number of rows returned by the list query.
- Deny inactive users with the admin role access to admin views.
- Reject AJAX inline updates when the view disables editing.
- Isolate extension shutdown exceptions so the remaining extensions
  still close.
- Log only the email type and a masked recipient when no sender is
  registered, instead of the full payload.
- Refuse login for disabled accounts and invalidate their existing
  sessions in ``user_loader``.

0.4.1 - 2026-11-11
------------------

Changed
~~~~~~~

- Use uv for development setup and dependency management; installing
  development dependencies with pip is deprecated.
- Require WTForms 3.3.2 or later.

Fixed
~~~~~

- Format ``time`` and ``datetime`` values in admin views as ``HH:MM:SS`` and
  ``YYYY-MM-DD HH:MM:SS``.
- Avoid WTForms 3.3 deprecation warnings and support string, dict,
  callable, and three-item tuple ``choices`` in ``ChoiceField``, while
  preserving ``render_kw`` and ``optgroup`` when rendering.

0.4.0 - 2026-11-04
------------------

Added
~~~~~

- Add inline-model support to views.

Fixed
~~~~~

- Show the decrypted TOTP secret during authenticator setup.

0.3.1 - 2026-10-11
------------------

Added
~~~~~

- Add reusable modal form flows and improve two-factor authentication setup.

Changed
~~~~~~~

- Improve SQLAlchemy lifecycle management, session configuration, and in-memory
  SQLite support.
- Allow extensions to provide admin views for automatic registration, and
  clarify duplicate extension-name errors.

0.3.0 - 2026-10-07
------------------

Added
~~~~~

- Add user registration, login, logout, profile management, and user-center
  views.
- Add email verification, email change, password reset, and recovery
  workflows.
- Add a SQLAlchemy-backed user store with user profiles and role management.
- Add authentication and role-based authorization.
- Add TOTP-based two-factor authentication and recovery codes.

0.2.0 - 2026-01-07
------------------

Added
~~~~~

- Add an extension system with registration, dependency management, and
  lifecycle hooks.
- Add an admin interface with model views, CRUD operations, filtering, sorting,
  pagination, and data export.
- Add SQLAlchemy integration for database access, model forms, relationships,
  and queries.
- Add form fields, widgets, validators, and CSRF protection.
- Add email delivery and notification support.
- Add frontend plugin management and Bootstrap-based components.
- Add Babel integration for localization.

0.1.0 - 2024-03-20
------------------

Added
~~~~~

- Initial release of the Flask-Exts package and documentation.
