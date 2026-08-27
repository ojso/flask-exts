from typing import List
from markupsafe import Markup
from operator import attrgetter
import os
import importlib
from flask import g

# import inspect
from .plugin_base import PluginBase


class PluginManager:
    def __init__(self):
        self._registry = {}
        self._default_plugins = []

    def set_default_plugins(self, names: List[str]):
        for name in names:
            if name not in self._default_plugins and name in self._registry:
                self._default_plugins.append(name)

    def init_app(self, app):
        plugins_directory = os.path.join(os.path.dirname(__file__), "plugins")
        namespace = f"{__package__}.plugins"
        self.load_from_directory(plugins_directory, namespace, PluginBase)
        self.init_plugins()

    def get_request_plugins(self):
        if not hasattr(g, "_request_plugins"):
            g._request_plugins = []
        return g._request_plugins

    def add_request_plugins(self, names: List[str] | str) -> None:
        """
        Add plugins to the current request plugins in flask.g.
        """
        if not isinstance(names, list):
            names = [names]

        request_plugins = self.get_request_plugins()
        for name in names:
            if name not in self._default_plugins and name not in request_plugins:
                request_plugins.append(name)

    def load_css(self):
        css_links = [
            f'<link rel="stylesheet" href="{css}">'
            for name in (self._default_plugins + self.get_request_plugins())
            if (plugin := self._registry.get(name)) and (css := plugin.css())
        ]
        css = "\n".join(css_links)
        return Markup(css)

    def load_js(self):
        plugins = [
            self._registry.get(name)
            for name in self._default_plugins + self.get_request_plugins()
            if name in self._registry
        ]
        js_links = [
            f'<script src="{js}"></script>'
            for plugin in sorted(plugins, key=attrgetter("weight"), reverse=True)
            if (js := plugin.js())
        ]
        js = "\n".join(js_links)
        return Markup(js)

    def register_plugin(self, plugin):
        self._registry[plugin.name] = plugin

    def load_from_directory(self, directory, namespace, base_class):
        """
        Scans the specified directory for Python files, imports them.

        :param directory: The directory to scan for Python files.
        :param namespace: The namespace of plugins.
        :param base_class: The base class that plugins should inherit from.
        :return: None
        """
        for filename in os.listdir(directory):
            if (
                filename.endswith("plugin.py")
                and filename != "plugin.py"
                and not filename.startswith("__")
            ):
                module_name = filename[:-3]
                _module = importlib.import_module(f"{namespace}.{module_name}")

    def init_plugins(self):
        for _, plugin_cls in PluginBase.get_registry().items():
            plugin = plugin_cls()
            self.register_plugin(plugin)
