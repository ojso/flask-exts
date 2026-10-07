import importlib
import os

from flask import g
from markupsafe import Markup

from .plugin_base import PluginBase


class PluginCycleError(Exception):
    pass


class PluginManager:
    def __init__(self):
        self._registry = {}
        self._default_plugins = []

    def init_app(self, app):
        plugins_directory = os.path.join(os.path.dirname(__file__), "plugins")
        namespace = f"{__package__}.plugins"
        self.load_from_directory(plugins_directory, namespace, PluginBase)
        self.init_plugins()

    def init_plugins(self):
        for plugin_cls in PluginBase.get_registry().values():
            plugin = plugin_cls()
            self.register_plugin(plugin)

    def register_plugin(self, plugin):
        if plugin.name in self._registry:
            raise ValueError(f"Plugin with name '{plugin.name}' is already registered.")
        self._registry[plugin.name] = plugin

    def set_default_plugins(self, names: list[str]):
        for name in names:
            if name not in self._default_plugins and name in self._registry:
                self._default_plugins.append(name)

    def get_request_plugins(self) -> list[str]:
        if not hasattr(g, "_request_plugins"):
            g._request_plugins = []
        return g._request_plugins

    def add_request_plugins(self, names: list[str]) -> None:
        """
        Add plugins to the current request plugins in flask.g.
        """
        request_plugins = self.get_request_plugins()
        for name in names:
            if name not in self._default_plugins and name not in request_plugins:
                request_plugins.append(name)

    def ordered_names(self):
        """
        Returns the names of the active plugins in the order they should be loaded,
        considering their dependencies.
        """
        names = self._default_plugins + self.get_request_plugins()
        resolved, done, in_progress = [], set(), []

        def visit(name):
            if name in done:
                return
            if name in in_progress:
                cycle = " -> ".join(in_progress[in_progress.index(name) :] + [name])
                raise PluginCycleError(f"Circular plugin dependency: {cycle}")
            plugin = self._registry.get(name)
            if plugin is None:
                raise ValueError(f"Plugin '{name}' is not registered.")
            in_progress.append(name)
            for dep in plugin.dependencies:
                visit(dep)
            in_progress.pop()
            done.add(name)
            resolved.append(name)

        for name in names:
            visit(name)
        return resolved

    def load_styles(self):
        parts = []
        for name in self.ordered_names():
            part = self._registry[name].style()
            if part:
                parts.append(part)
        return Markup("\n".join(parts))

    def load_scripts(self):
        parts = []
        for name in self.ordered_names():
            part = self._registry[name].script()
            if part:
                parts.append(part)
        return Markup("\n".join(parts))

    def load_from_directory(self, directory, namespace, base_class):
        """
        Scans the specified directory for Python files, imports them.

        Args:
            directory: The directory to scan for Python files.
            namespace: The namespace of plugins.
            base_class: The base class that plugins should inherit from.

        Returns:
            None
        """
        for filename in os.listdir(directory):
            if (
                filename.endswith("plugin.py")
                and filename != "plugin.py"
                and not filename.startswith("__")
            ):
                module_name = filename[:-3]
                _module = importlib.import_module(f"{namespace}.{module_name}")
