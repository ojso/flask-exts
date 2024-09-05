from flask import Blueprint
from .bootstrap import Bootstrap
from .csrf import generate_csrf

bootstrap = Bootstrap()


def template_init_app(app):

    if not hasattr(app, "extensions"):
        app.extensions = {}
    app.extensions["templating"] = "none"

    blueprint = Blueprint("templating", __name__, template_folder="../templates")
    app.register_blueprint(blueprint)

    app.jinja_env.globals["csrf_token"] = generate_csrf

    template_name = app.config.get("TEMPLATE_NAME")
    
    if template_name == "bootstrap":
        bootstrap.init_app(app)
