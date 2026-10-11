Flask-Exts
==========

Flask-Exts is a toolkit for building Flask applications with an integrated
admin interface, SQLAlchemy support, forms, localization, and user-account
features. It brings common application components together behind a
dependency-aware extension system. The project is inspired by
`Flask-Admin <https://github.com/pallets-eco/flask-admin/>`_ and
`Bootstrap <https://getbootstrap.com/>`_.

Highlights
----------

- **Modern frontend:** Uses Bootstrap 5 and native browser APIs, with no
  jQuery dependency or Bootstrap 4 frontend.
- **Composable extensions:** Initializes extensions in dependency order and
  lets extensions contribute views to the admin interface.
- **Built-in account features:** Provides authentication, email verification
  and recovery flows, TOTP-based two-factor authentication, and recovery
  codes.
- **Integrated admin and data tools:** Includes SQLAlchemy integration,
  model management, forms, filtering, and data export.
- **Localization support:** Integrates Babel for translating application
  interfaces.

Installation
------------

Flask-Exts requires Python 3.10 or later. Install it with pip:

.. code-block:: console

   pip install flask-exts

Quick start
-----------

Create a Flask application and initialize the extension manager:

.. code-block:: python

   from flask import Flask
   from flask_exts import ExtensionManager

   app = Flask(__name__)
   app.config["SECRET_KEY"] = "change-this-for-local-development"
   app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.sqlite"

   extensions = ExtensionManager()
   extensions.init_app(app)

   if __name__ == "__main__":
       app.run(debug=True)

For a complete example with a custom admin view and database setup, see
``examples/simple``.

Documentation
-------------

- `Documentation <https://flask-exts.readthedocs.io/>`_
- `Runnable examples <https://github.com/ojso/flask-exts/tree/main/examples>`_
- `Changelog <https://flask-exts.readthedocs.io/en/latest/changes.html>`_

License
-------

Flask-Exts is distributed under the terms of the
`MIT License <https://opensource.org/licenses/MIT>`_.
