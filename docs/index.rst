.. Flask-Exts documentation master file, created by
   sphinx-quickstart on Fri Mar 22 06:29:14 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Flask-Exts's documentation!
======================================

**Flask-Exts** is a Flask extensions with admin, SQLAlchemy, babel, forms, fields, widgets, and so on.

.. _installation:

Installation
==============

To use Flask-Exts, first install it using pip:

.. code-block:: console

   (.venv) $ pip install flask-exts

Usage
======

.. code-block:: python

   from flask_exts import Manager
   from flask import Flask   

   manager = Manager()
   app = Flask(__name__)

   # init Manager
   manager.init_app(app)

More examples please goto :doc:`examples`.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   configure
   develop
   examples
   changes

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
