============
templating
============

bootstrap
============

.. code-block:: python

    from flask import Flask
    from flask_exts import Manager   

    app = Flask(__name__)
    manager = Manager()

    # set bootstrap 
    app.config["TEMPLATE_NAME"] = "bootstrap"
    app.config["BOOTSTRAP_VERSION"] = 4  # or 5. Default is 4.

    # set local css and js urls. Default is cdn:https://cdn.jsdelivr.net/npm.
    app.config["JQUERY_JS_URL"] = "/vendor/jquery/dist/jquery.slim.js"
    app.config["BOOTSTRAP_CSS_URL"] = "/vendor/bootstrap4/dist/css/bootstrap.css"
    app.config["BOOTSTRAP_JS_URL"] = "/vendor/bootstrap4/dist/js/bootstrap.bundle.js"

    # icon sprite
    app.config["ICON_SPRITE_URL"] = "/vendor/bootstrap-icons/bootstrap-icons.svg"

    # init Manager
    manager.init_app(app)

templates
---------------

To load css and js.

.. code-block:: jinja

    {{ bootstrap.load_css() }}
    {{ bootstrap.load_js() }}
