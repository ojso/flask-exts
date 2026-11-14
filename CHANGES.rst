Changelog
=========

All notable changes to this project are documented in this file.

Unreleased
----------

Added
~~~~~

- Add the ``jwt_encode_for_user`` and ``password_fingerprint`` helpers for
  issuing access tokens bound to a user's current credentials.
- Add the ``JWT_LEEWAY`` configuration to tolerate clock skew when validating
  tokens.

Changed
~~~~~~~

- **Breaking:** ``load_user_from_request`` now rejects Bearer tokens without a
  ``pwd`` claim and requires ``amr`` to contain ``otp`` for TFA-enabled users.
  Previously issued tokens are therefore invalid after upgrading.
- **Breaking:** JWT signing and validation are restricted to ``HS256``,
  ``HS384``, and ``HS512``. Configuring ``JWT_HASH`` to another value,
  including ``none``, raises ``RuntimeError`` at first use.
- **Breaking:** ``JWT_SECRET_KEY`` must be set before JWT use, be at least 32
  bytes, and differ from ``SECRET_KEY``.
- ``jwt_encode`` now writes an ``iat`` claim, and ``jwt_decode`` honours
  ``JWT_LEEWAY``.
- ``Authorization`` accepts the ``Bearer`` scheme case-insensitively.
- ``jwt_encode_for_user`` treats a string ``amr`` value as one method and
  rejects non-string entries.

Fixed
~~~~~

- Reject non-integer JWT ``id`` claims such as ``true`` and ``1.9`` instead of
  resolving them to a different user id.
- Avoid splitting ``amr="otp"`` into individual characters.

Security
~~~~~~~~

- Bind JWT access tokens to the current password hash so password changes and
  resets invalidate previously issued tokens (SEC-08).
- Require completed second-factor authentication in the ``amr`` claim for
  TFA-enabled users (SEC-02).

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
