from .registry import PluginRegistry


class LifecycleManager:
    """English: Single responsibility manage plugin startup shutdown / Single responsibility: manage plugin startup/shutdown lifecycle / 单一职责：管理插件的启动/停止生命周期"""

    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        self._active = set()

    def activate(self, namespace=None, context=None):
        """English: Activate plugins / Activate plugins / 激活插件"""
        plugins = self.registry.get_all(namespace)
        for full_name, plugin in plugins.items():
            if full_name not in self._active:
                try:
                    if context and hasattr(plugin, "setup"):
                        plugin.setup(context)
                    if hasattr(plugin, "activate"):
                        plugin.activate()
                    self._active.add(full_name)
                except Exception as e:
                    raise

    def deactivate(self, namespace=None):
        """English: Deactivate plugins / Deactivate plugins / 停用插件"""
        plugins = self.registry.get_all(namespace)
        for full_name, plugin in reversed(list(plugins.items())):
            if full_name in self._active:
                if hasattr(plugin, "deactivate"):
                    plugin.deactivate()
                self._active.discard(full_name)

    def is_active(self, namespace, name):
        return f"{namespace}.{name}" in self._active
