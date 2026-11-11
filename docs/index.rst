Welcome to Flask-Exts's documentation!
======================================

**Flask-Exts** provides reusable extensions for Flask applications, including
admin tools, SQLAlchemy support, forms, and localization.

Highlights
----------

- Extensions initialize in dependency order and can add admin views.
- Includes account authentication, email verification, and two-factor
  authentication.
- Provides SQLAlchemy tools, forms, filtering, and data export.
- Supports interface translation with Babel.

Getting started
---------------

Flask-Exts requires Python 3.11 or later. Add it to your project with uv:

.. _installation:

.. code-block:: console

   uv add flask-exts

With pip:

.. code-block:: console

   pip install flask-exts

Initialize the extension manager in your Flask application:

.. code-block:: python

   from flask import Flask
   from flask_exts import ExtensionManager

   app = Flask(__name__)
   app.config["SECRET_KEY"] = "change-this-for-local-development"
   app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.sqlite"

   extensions = ExtensionManager()
   extensions.init_app(app)

See :doc:`quickstart` for a complete example.

Documentation guide
-------------------

- :doc:`quickstart` — installation and first application.
- :doc:`configure` — configuration options.
- :doc:`examples` — sample applications.
- :doc:`advanced/index` — advanced usage.
- :doc:`develop` — contributing and development.
- :doc:`testing` — test commands and conventions.
- :doc:`changes` — release history.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   configure
   examples
   advanced/index
   develop
   testing
   changes

.. toctree::
   :maxdepth: 1

   api

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
