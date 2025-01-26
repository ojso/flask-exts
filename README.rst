Flask Exts
==========

Flask-Exts is mainly inspired by:

- `WTForms <https://github.com/wtforms/wtforms/>`_
- `Flask-Admin <https://github.com/flask-admin/flask-admin/>`_

Flask-Exts is part rewrited from above and well tested.

License
-------

Flask-Exts is distributed under the terms of the `MIT <https://opensource.org/licenses/MIT>`_.


Installation
------------

Install and update using pip:

.. code-block:: console

    $ pip install -U Flask-Exts

Examples
----------

.. code-block:: python

    from flask import Flask
    from flask_exts import Manager

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"
    # Manager init
    manager = Manager()
    manager.init_app(app)

    if __name__ == "__main__":
        app.run(debug=True)

