from .base import PluginBase
from .registry import PluginRegistry
from .loader import PluginLoader
from .lifecycle import LifecycleManager

class PluginEngine:
    """插件引擎：加载、初始化、管理生命周期"""

    def __init__(self):
        self.registry = PluginRegistry()

    def load_from_directory(self, directory: str, namespace: str):
        """从目录加载插件"""
        import importlib, os, sys

        sys.path.insert(0, os.path.dirname(directory))
        for filename in os.listdir(directory):
            if filename.endswith(".py") and not filename.startswith("_"):
                module_name = filename[:-3]
                spec = importlib.util.spec_from_file_location(
                    module_name, os.path.join(directory, filename)
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # 找到 PluginBase 的子类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, PluginBase)
                        and attr is not PluginBase
                    ):
                        plugin = attr()
                        plugin.namespace = namespace
                        if not plugin.name:
                            plugin.name = module_name
                        self.registry.register(plugin)
                        print(f"  ✓ 加载插件: {namespace}.{plugin.name}")

    def activate_all(self, namespace: str = None):
        """激活插件"""
        plugins = self.registry.get_all(namespace)
        for name, plugin in plugins.items():
            plugin.activate()
            print(f"  ✓ 激活: {name}")


class PluginEngine:
    """
    单一职责：协调其他组件（Facade 模式）。
    自己不做事，只负责把事情分给正确的组件。
    """

    def __init__(self):
        self.registry = PluginRegistry()
        self.loader = PluginLoader()
        self.lifecycle = LifecycleManager(self.registry)

    def load_and_register(self, directory, namespace, base_class):
        """加载 + 注册（编排两个组件）"""
        plugins = self.loader.load_from_directory(directory, namespace, base_class)
        for plugin in plugins:
            self.registry.register(plugin)
        return plugins

    def activate(self, namespace=None, context=None):
        self.lifecycle.activate(namespace, context)

    def deactivate(self, namespace=None):
        self.lifecycle.deactivate(namespace)

    def get(self, namespace, name):
        return self.registry.get(namespace, name)



