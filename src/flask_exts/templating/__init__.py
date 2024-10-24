import os.path as op
from flask import Blueprint
from ..utils.form import is_hidden_field
from ..utils.form import is_required_form_field
from ..utils.form import get_table_titles
from ..utils.csrf import generate_csrf
from .theme import DefaultTheme


def template_init_app(app):

    blueprint = Blueprint(
        "template",
        __name__,
        url_prefix="/template",
        template_folder=op.join("..", "templates"),
        static_folder=op.join("..", "static"),
        # static_url_path='/template/static',
    )
    app.register_blueprint(blueprint)

    app.jinja_env.globals["csrf_token"] = generate_csrf
    app.jinja_env.globals["is_hidden_field"] = is_hidden_field
    app.jinja_env.globals["is_required_form_field"] = is_required_form_field
    app.jinja_env.globals["get_table_titles"] = get_table_titles

    if app.config.get("TEMPLATE_THEME"):
        theme = app.config.get("TEMPLATE_THEME")
    else:
        theme = DefaultTheme()

    app.extensions["template"] = theme

    app.jinja_env.globals["theme"] = theme

    # app.config.setdefault("BOOTSTRAP_TABLE_VIEW_TITLE", "View")
    # app.config.setdefault("BOOTSTRAP_TABLE_EDIT_TITLE", "Edit")
    # app.config.setdefault("BOOTSTRAP_TABLE_DELETE_TITLE", "Delete")
    # app.config.setdefault("BOOTSTRAP_TABLE_NEW_TITLE", "New")

    # @app.context_processor
    # def get_theme():
    #     return {"theme": theme}
