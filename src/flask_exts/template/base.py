import os.path as op
from flask import Blueprint
from .theme import BootstrapTheme
from .utils import type_name
from .utils import is_hidden_field
from .utils import is_required_form_field
from .utils import get_table_titles
from .form.csrf import get_or_generate_csrf_token as csrf_token


class Template:
    """Template extension for Flask applications."""

    def __init__(self, app=None):
        self.app = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.init_blueprint(app)

        self.theme = self.get_theme()
        app.jinja_env.globals["template"] = self.theme

        app.jinja_env.globals["type_name"] = type_name
        app.jinja_env.globals["is_hidden_field"] = is_hidden_field
        app.jinja_env.globals["is_required_form_field"] = is_required_form_field
        app.jinja_env.globals["get_table_titles"] = get_table_titles
        app.jinja_env.globals["csrf_token"] = csrf_token

    def get_theme(self):
        return BootstrapTheme()

    def init_blueprint(self, app):
        blueprint = Blueprint(
            "template",
            __name__,
            url_prefix="/template",
            template_folder=op.join("..", "templates"),
            static_folder=op.join("..", "static"),
            # static_url_path='/template/static',
        )
        app.register_blueprint(blueprint)

        # @app.context_processor
        # def get_template():
        #     return {"template": theme}
