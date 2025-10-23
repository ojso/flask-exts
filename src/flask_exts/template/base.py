from .funcs import Funcs
from ..themes.theme import ThemeManager


class Template:
    """Template extension for Flask applications."""

    def __init__(self, app=None):
        self.app = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        app.jinja_env.globals["_template"] = self
        self.theme = ThemeManager()
        self.theme.init_app(app)
        self.funcs = Funcs()
