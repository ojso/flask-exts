from typing import ClassVar


class PluginBase:
    _registry: ClassVar[dict] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        PluginBase._registry[cls.__name__] = cls

    @classmethod
    def get_registry(cls):
        return PluginBase._registry

    def __init__(self, name, version=None, dependencies=()):
        self.name = name
        self.version = version
        self.dependencies = list(dependencies)

    def style(self):
        return ""

    def script(self):
        return ""
