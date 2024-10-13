============
templating
============

bootstrap4
===================

Default is bootstrap4

bootstrap5
============

.. code-block:: python

    from flask import Flask
    from flask_exts import Manager
    from flask_exts.templating.theme import DefaultTheme

    bootstrap5_theme = DefaultTheme(bootstrap_version=5)

    app = Flask(__name__)
    manager = Manager()

    # set bootstrap 5
    app.config["TEMPLATE_THEME"] = bootstrap5_theme 

    # init Manager
    manager.init_app(app)

