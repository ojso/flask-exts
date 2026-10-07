from .plugin_manager import PluginManager


class Template:
    """Template extension for Flask applications."""

    def init_app(self, app):
        self.app = app
        self.init_plugins(app)

    def init_plugins(self, app):
        self.plugin_manager = PluginManager()
        self.plugin_manager.init_app(app)
