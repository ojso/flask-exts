from flask import Blueprint
from ..utils.form import is_hidden_field, get_table_titles
from ..utils.csrf import generate_csrf


def template_init_app(app):

    if not hasattr(app, "extensions"):
        app.extensions = {}
    app.extensions["templating"] = "none"

    blueprint = Blueprint("templating", __name__, template_folder="../templates")
    app.register_blueprint(blueprint)

    app.jinja_env.globals["csrf_token"] = generate_csrf
    app.jinja_env.globals["is_hidden_field"] = is_hidden_field
    app.jinja_env.globals["get_table_titles"] = get_table_titles

    template_name = app.config.get("TEMPLATE_NAME")

    if template_name == "bootstrap":
        from .bootstrap import Bootstrap

        bootstrap = Bootstrap()
        bootstrap.init_app(app)
