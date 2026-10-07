Quickstart
==========

This guide walks you through installing Flask-Exts and running a minimal Flask
application with an admin panel. For more complete examples, including user
authentication and database-driven management, see :doc:`examples`.

Prerequisites
-------------

- Python 3.10+
- Basic knowledge of Flask and SQLAlchemy

Installation
------------

Install the package with pip:

.. code-block:: console

   pip install flask-exts

Minimal application
-------------------

The simplest Flask-Exts application looks like this:

.. literalinclude:: ../examples/simple/__init__.py
   :language: python

Run the app:

.. code-block:: console

   python app.py

Then open ``http://localhost:5000/`` in your browser to view the admin page.

About the example
------------------

The example registers a lightweight admin view, initializes the Flask extension
manager, and creates the database tables in an application context. This is a
good starting point for building a full application with custom admin pages and
database models.

Next steps
----------

- See :doc:`configure` for the available configuration options.
- See :doc:`examples` for runnable demo applications.
- See :doc:`advanced/index` for more advanced patterns.
