Changelog
=========

All notable changes to this project are documented in this file.

Unreleased
----------

Changed
~~~~~~~

- Model timestamps and login-lockout timestamps are timezone-aware UTC.
  Databases without timezone support store the UTC wall time; existing rows
  are interpreted as UTC.
- CSV and tablib exports continue to write values as-is. Spreadsheet
  formula-injection neutralization is intentionally not applied.

Fixed
~~~~~

- ``FileSize`` validates using ``Content-Length`` or a seek-to-end lookup
  instead of reading the whole upload into memory.
- Negative ``page`` and ajax ``offset`` values are clamped to zero.
- Pagination links preserve the zero-based page number, so the second page and
  later pages open the requested page.
- The default admin view is the first exposed ``/`` or ``/index/`` method
  instead of the last one returned by ``inspect.getmembers``.
- ``User.get_or_create_totp_secret`` flushes instead of committing.
- Boolean admin formatters escape the generated title attribute.
- ``Security.init_app`` explains that ``SECRET_KEY`` must be configured first.
- Token serializers without an explicit default use 30 minutes instead of 7
  days.

Security
~~~~~~~~

- CSRF session tokens use ``secrets.token_urlsafe`` instead of SHA-1.
- JWT decoding requires the ``iat`` claim.

0.4.3 - 2026-11-15
------------------

Added
~~~~~

- Add ``jwt_encode_for_user`` and ``password_fingerprint`` helpers, plus the
  ``JWT_LEEWAY`` configuration.
- Add safe response-header defaults and ``SECURITY_REQUIRE_HTTPS``, governed by
  the ``SECURITY_*`` settings.
- Add ``SECURITY_COOKIE_DEFAULTS_ENABLED`` to opt out of the Cookie defaults;
  invalid ``SECURITY_HEADERS`` or ``SECURITY_HSTS`` values now fail at
  startup instead of on every response.

Changed
~~~~~~~

- **Breaking:** JWT handling is hardened: ``HS256``/``HS384``/``HS512`` only,
  a dedicated ``JWT_SECRET_KEY`` of at least 32 bytes, an ``iat`` claim,
  strict ``id``/``amr`` parsing, and case-insensitive ``Bearer``.
- **Breaking:** ``load_user_from_request`` requires a ``pwd`` fingerprint and
  rejects older tokens; TFA-enabled users must also present ``amr`` with
  ``otp``.
- ``SESSION_COOKIE_SAMESITE`` and ``REMEMBER_COOKIE_SAMESITE`` default to
  ``Lax``; both and the response headers can be overridden.

Security
~~~~~~~~

- Bind tokens to the current password hash, require second-factor
  authentication, and apply secure Cookie/header defaults.

0.4.2 - 2026-11-13
------------------

Added
~~~~~

- Add failed-login lockout to ``SqlaUserStore``: ``users`` gains
  ``failed_login_count`` and ``locked_until``, password and second-factor
  failures share the counter, and the delay doubles up to a configurable cap.
- Add the login contract to ``UserStore``
  (``login_user_by_username_password``, ``is_locked``,
  ``record_login_failure``, ``clear_login_failures``) so custom stores can
  provide the same lockout behavior.

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
