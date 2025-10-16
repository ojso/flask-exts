import os.path as op
from flask import Blueprint
from markupsafe import Markup
from .funcs import Funcs
from .theme import Theme
from .plugins.plugin_manager import PluginManager


class Template:
    """Template extension for Flask applications."""

    def __init__(self, app=None):
        self.app = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        app.jinja_env.globals["_template"] = self
        self.funcs = Funcs()
        self.theme = Theme()
        self.plugin = PluginManager()
        self.init_blueprint(app)
        self.init_plugins(app)

    def init_blueprint(self, app):
        blueprint = Blueprint(
            "_template",
            __name__,
            url_prefix="/template",
            template_folder=op.join("./themes/default", "templates"),
            static_folder=op.join("./themes/default", "static"),
        )
        app.register_blueprint(blueprint)

    def init_plugins(self, app):
        from .plugins.copybutton_plugin import CopyButtonPlugin
        from .plugins.jquery_plugin import jQueryPlugin
        from .plugins.bootstrap4_plugin import Bootstrap4Plugin
        from .plugins.qrcode_plugin import QRCodePlugin

        self.plugin.register_plugins(
            [
                jQueryPlugin(),
                Bootstrap4Plugin(),
                QRCodePlugin(),
                CopyButtonPlugin(),
            ]
        )
        self.plugin.enable_plugin(["jquery", "bootstrap4"])

    def load_all_css(self):
        css = ""
        for name in self.plugin.enabled_plugins:
            plugin = self.plugin.plugins.get(name)
            if css:
                css += "\n"
            css += f'<link rel="stylesheet" href="{plugin.css()}">'
        return Markup(css)

    def load_all_js(self):
        js = ""
        for name in self.plugin.enabled_plugins:
            plugin = self.plugin.plugins.get(name)
            if js:
                js += "\n"
            js += f'<script src="{plugin.js()}"></script>'
        return Markup(js)
