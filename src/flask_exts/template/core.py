import os.path as op
from flask import Blueprint
from ..html_plugins.plugin_manager import PluginManager
from .theme import Theme
from ..forms.form.csrf import get_csrf_token

class Template:
    """Template extension for Flask applications."""

    def __init__(self, app=None):
        self.app = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        app.jinja_env.globals["_template"] = self
        self.init_template_blueprint(app)
        self.init_plugins(app)
        self.init_theme(app)
        app.jinja_env.globals["csrf_token"] = get_csrf_token
        app.jinja_env.add_extension("jinja2.ext.do")
        # app.extensions["exts"].template.plugin_manager.enable_plugin(["bootstrap5"])
        # app.jinja_env.add_extension('jinja2.ext.debug')

    def init_template_blueprint(self, app):
        blueprint = Blueprint(
            "_template",
            __name__,
            url_prefix="/template",
            template_folder="../templates",
            static_folder="../static",
        )
        app.register_blueprint(blueprint)

    def init_plugins(self, app):
        self.plugin_manager = PluginManager()
        self.plugin_manager.init_app(app)

    def init_theme(self, app):
        self.theme = Theme()
        self.theme.init_app(app)
