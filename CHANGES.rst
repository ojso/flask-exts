Changelog
=========

All notable changes to this project are documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.1.0/>`_
and this project adheres to
`Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Unreleased
----------

Fixed
~~~~~

- Format ``time`` and ``datetime`` values in admin views as ``HH:MM:SS`` and
  ``YYYY-MM-DD HH:MM:SS``.

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
