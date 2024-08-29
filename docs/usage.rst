=====
Usage
=====

.. _installation:

Installation
==============

To use Flask-Exts, first install it using pip:

.. code-block:: console

   (.venv) $ pip install flask-exts


Start
======

.. code-block:: python

   from flask_exts import Manager
   from flask import Flask   

   manager = Manager()
   app = Flask(__name__)

   # init Manager
   manager.init_app(app)
