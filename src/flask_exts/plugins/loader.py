import os
import importlib
import importlib.util
import sys

class PluginLoader:
    """English: Single responsibility load plugins from the / Single responsibility: load plugins from the file system / 单一职责：从文件系统加载插件"""

    @staticmethod
    def load_from_directory(directory, namespace, base_class):
        """English: Load all plugin classes from the / Load all plugin classes from the directory / 从目录加载所有插件类"""
        import importlib, importlib.util, os, sys

        if not os.path.isdir(directory):
            return []

        loaded = []
        sys.path.insert(0, os.path.dirname(directory))

        for filename in sorted(os.listdir(directory)):
            if filename.endswith(".py") and not filename.startswith("_"):
                filepath = os.path.join(directory, filename)
                spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, base_class)
                        and attr is not base_class
                    ):
                        plugin = attr()
                        plugin.namespace = namespace
                        if not plugin.name:
                            plugin.name = filename[:-3]
                        loaded.append(plugin)

        return loaded
