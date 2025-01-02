import os.path as op
from flask import Blueprint
from .utils import is_hidden_field
from .utils import is_required_form_field
from .utils import get_table_titles
from .utils import generate_csrf
from .theme import BootstrapTheme


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
    
    app.jinja_env.globals["is_hidden_field"] = is_hidden_field
    app.jinja_env.globals["is_required_form_field"] = is_required_form_field
    app.jinja_env.globals["get_table_titles"] = get_table_titles
    app.jinja_env.globals["csrf_token"] = generate_csrf

    theme = app.config.get("TEMPLATE_THEME",BootstrapTheme())

    app.extensions["template"] = theme
    app.jinja_env.globals["template"] = theme


    # @app.context_processor
    # def get_template():
    #     return {"template": theme}
