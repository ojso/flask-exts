from markupsafe import Markup
import os
import sys
import importlib.util
import inspect
from .base_plugin import BasePlugin


class PluginManager:
    def __init__(self):
        self.registered_plugins = {}
        self.enabled_plugins = []

    def register_plugin(self, plugin):
        self.registered_plugins[plugin.name] = plugin

    def enable_plugin(self, names):
        if isinstance(names, str):
            names = [names]
        for name in names:
            if name not in self.enabled_plugins and name in self.registered_plugins:
                self.enabled_plugins.append(name)

    def init_app(self, app):
        # Register plugins
        plugins_directory = os.path.dirname(__file__)
        self.load_plugins_in_directory(plugins_directory, BasePlugin)
        # print("registered plugins:", [k for k in self.registered_plugins])

    def load_css(self):
        css_links = [
            f'<link rel="stylesheet" href="{css}">'
            for name in self.enabled_plugins
            if (plugin := self.registered_plugins.get(name)) and (css := plugin.css())
        ]
        css = "\n".join(css_links)
        return Markup(css)

    def load_js(self):
        js_links = [
            f'<script src="{js}"></script>'
            for name in self.enabled_plugins
            if (plugin := self.registered_plugins.get(name)) and (js := plugin.js())
        ]
        js = "\n".join(js_links)
        return Markup(js)

    def load_plugins_in_directory(self, directory, base_class):
        """
        Scans the specified directory for Python files, imports them,
        and returns a list of subclasses of the specified base class.

        :param directory: The directory to scan for Python files.
        :param base_class: The base class to find subclasses of.
        :return: A list of subclasses of the specified base class.
        """
        subclasses = []

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
                    # sys.modules[module_name] = module
                    spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, base_class) and obj is not base_class:
                        subclasses.append((name, obj))
                        plugin_instance = obj()
                        self.register_plugin(plugin_instance)

        # print(subclasses)
