import os.path as op
from flask import Blueprint
from .funcs import Funcs
from .plugins.plugin_manager import PluginManager
from .theme import Theme


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
        self.init_funcs(app)
        self.init_plugins(app)

        self.init_theme(app)

    def init_template_blueprint(self, app):
        blueprint = Blueprint(
            "_template",
            __name__,
            url_prefix="/template",
            template_folder="../templates",
            static_folder="../static",
        )
        app.register_blueprint(blueprint)

    def init_funcs(self, app):
        self.funcs = Funcs()

    def init_plugins(self, app):
        self.plugin_manager = PluginManager()
        self.plugin_manager.init_app(app)

    def init_theme(self, app):
        self.theme = Theme()
        self.theme.init_app(app)
