.. Flask-Exts documentation master file, created by
   sphinx-quickstart on Fri Mar 22 06:29:14 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Flask-Exts's documentation!
======================================

English / 中文
----------------
This page is provided in English with a Chinese summary for easier reading.
中文说明：本页面保留英文原文，并附带中文说明，便于中英文对照阅读。


**Flask-Exts** is a Flask extensions with SQLAlchemy, babel, forms, fields, widgets, and so on.

中文说明：Flask-Exts 是一个基于 Flask 的扩展集合，提供 SQLAlchemy、Babel、表单、字段、小组件和后台管理等能力，便于快速搭建完整的 Web 应用。
English summary: Flask-Exts is a Flask extension toolkit that brings together SQLAlchemy, Babel, forms, fields, widgets, and admin features to help build complete web applications faster.

Flask-Exts is mainly inspired by:

- `Bootstrap <https://getbootstrap.com/>`_
- `Flask-Admin <https://github.com/pallets-eco/flask-admin/>`_

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

.. literalinclude:: ../examples/simple/__init__.py
  :language: python

More examples, please click :doc:`examples`.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started
   admin_modelview
   configure
   develop
   examples
   advanced
   advanced_custom_plugins
   advanced_custom_fields
   performance
   theming
   security_advanced
   api
   changes

.. toctree::
   :maxdepth: 1

   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
