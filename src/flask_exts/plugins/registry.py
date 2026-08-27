from typing import Any
from .base import PluginBase


class PluginRegistry:
    """单一职责：管理插件的注册与查询，全局注册表，但按 namespace 隔离"""

    def __init__(self):
        self._plugins: dict[str, dict[str, Any]] = {}  # {namespace: {name: plugin}}

    def register(self, plugin: PluginBase):
        ns = plugin.namespace
        if ns not in self._plugins:
            self._plugins[ns] = {}
        self._plugins[ns][plugin.name] = plugin

    def unregister(self, namespace, name):
        self._plugins.get(namespace, {}).pop(name, None)

    def get(self, namespace: str, name: str):
        return self._plugins.get(namespace, {}).get(name)

    def get_all(self, namespace: str = None):
        if namespace:
            return self._plugins.get(namespace, {})
        # 返回所有
        result = {}
        for ns, plugins in self._plugins.items():
            for name, p in plugins.items():
                result[f"{ns}.{name}"] = p
        return result

    def has(self, namespace, name):
        return name in self._plugins.get(namespace, {})

    def list_namespaces(self):
        return list(self._plugins.keys())
