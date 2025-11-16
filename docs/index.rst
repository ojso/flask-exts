.. Flask-Exts documentation master file, created by
   sphinx-quickstart on Fri Mar 22 06:29:14 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Flask-Exts's documentation!
======================================

**Flask-Exts** is a Flask extensions with SQLAlchemy, babel, forms, fields, widgets, and so on.

Flask-Exts is mainly inspired by:

- `Bootstrap <https://getbootstrap.com/>`_
- `Flask-Admin <https://github.com/pallets-eco/flask-admin/>`_
- `Flask-Security <https://github.com/pallets-eco/flask-security/>`_

Flask-Exts is partially rewrited from above and well tested.

.. _installation:

Installation
==============

To use Flask-Exts, first install it using pip:

.. code-block:: console

   (.venv) $ pip install flask-exts

Examples
===========

``python simple.py`` to run a simple example.

.. literalinclude:: ../examples/simple.py
  :language: python

More examples, please click :doc:`examples`.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   configure
   develop
   examples
   changes

API Reference
-------------

If you are looking for information on a specific function, class or
method, this part of the documentation is for you.

.. toctree::
   :maxdepth: 1

   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
