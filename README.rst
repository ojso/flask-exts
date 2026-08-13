Flask Exts
==========

Flask-Exts is mainly inspired by:

- `Flask-Admin <https://github.com/pallets-eco/flask-admin/>`_
- `Bootstrap <https://getbootstrap.com/>`_


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
    from flask_exts import Exts

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"
    exts = Exts()
    exts.init_app(app)

    if __name__ == "__main__":
        app.run(debug=True)

