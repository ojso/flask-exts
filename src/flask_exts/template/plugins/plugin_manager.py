from markupsafe import Markup
import os
import importlib.util
# import inspect
from .base_plugin import PluginBase


class PluginManager:
    def __init__(self):
        self.plugins = {}
        self.enabled_plugins = []

    def enable_plugin(self, names):
        if isinstance(names, str):
            names = [names]
        for name in names:
            if name not in self.enabled_plugins and name in self.plugins:
                self.enabled_plugins.append(name)

    def init_app(self, app):
        plugins_directory = os.path.dirname(__file__)
        self._load_plugins_in_directory(plugins_directory, PluginBase)
        # print("init_subclass plugins:",PluginBase._plugins)
        self._init_plugins()
        

    def load_css(self):
        css_links = [
            f'<link rel="stylesheet" href="{css}">'
            for name in self.enabled_plugins
            if (plugin := self.plugins.get(name)) and (css := plugin.css())
        ]
        css = "\n".join(css_links)
        return Markup(css)

    def load_js(self):
        js_links = [
            f'<script src="{js}"></script>'
            for name in self.enabled_plugins
            if (plugin := self.plugins.get(name)) and (js := plugin.js())
        ]
        js = "\n".join(js_links)
        return Markup(js)

    def _register_plugin(self, plugin):
        self.plugins[plugin.name] = plugin

    def _load_plugins_in_directory(self, directory, base_class):
        """
        Scans the specified directory for Python files, imports them.

        :param directory: The directory to scan for Python files.
        :param base_class: The base class that plugins should inherit from.
        :return: None
        """
        for filename in os.listdir(directory):
            if (
                filename.endswith("plugin.py")
                and not filename.startswith("__")
                and filename != "base_plugin.py"
            ):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f"{__package__}.{module_name}")
                except:
                    module_path = os.path.join(directory, filename)
                    spec = importlib.util.spec_from_file_location(
                        module_name, module_path
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                # for name, obj in inspect.getmembers(module, inspect.isclass):
                #     if issubclass(obj, base_class) and obj is not base_class:
                #         plugin_instance = obj()
                #         self._register_plugin(plugin_instance)

    def _init_plugins(self):
        for _, plugin_cls in PluginBase._plugins.items():
            plugin_instance = plugin_cls()
            self._register_plugin(plugin_instance)

