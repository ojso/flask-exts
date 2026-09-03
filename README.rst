Flask Exts
==========

English / 中文
----------------
This page is provided in English with a Chinese summary for easier reading.
中文说明：本页面保留英文原文，并附带中文说明，便于中英文对照阅读。


Flask-Exts is mainly inspired by:

- `Flask-Admin <https://github.com/pallets-eco/flask-admin/>`_
- `Bootstrap <https://getbootstrap.com/>`_

中文说明：Flask-Exts 是一个基于 Flask 的扩展集合，整合 SQLAlchemy、表单、Babel 和后台管理等能力，适合快速构建现代 Web 应用。
English summary: Flask-Exts is a Flask extension toolkit that combines SQLAlchemy, forms, Babel, and admin features to help developers build modern web applications quickly.

License
-------

Flask-Exts is distributed under the terms of the `MIT <https://opensource.org/licenses/MIT>`_.


Installation
------------

Install and update using pip:

.. code-block:: console

    $ pip install Flask-Exts

Examples
----------

.. code-block:: python

    from flask import Flask
    from flask_exts import ExtensionManager

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"
    exts = ExtensionManager()
    exts.init_app(app)

    if __name__ == "__main__":
        app.run(debug=True)
