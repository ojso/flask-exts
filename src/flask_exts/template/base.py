import os.path as op
from flask import Blueprint
from .dataset import Dataset
from .funcs import Funcs
from .theme import BootstrapTheme
from .plugin import Plugin

class Template:
    """Template extension for Flask applications."""

    def __init__(self, app=None):
        self.app = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.init_blueprint(app)
        app.jinja_env.globals["template"] = self
        self.dataset = Dataset()
        self.funcs = Funcs()
        self.theme = self.get_theme()
        self.plugin = Plugin()
        
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
