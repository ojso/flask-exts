class PluginBase:
    _registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        PluginBase._registry[cls.__name__] = cls

    @classmethod
    def get_registry(cls):
        return PluginBase._registry

    @classmethod
    def get_plugin(cls, name):
        """Get a plugin class by name."""
        return PluginBase._registry.get(name)

    @classmethod
    def list_plugins(cls):
        """List all registered plugin names."""
        return list(PluginBase._registry.keys())

    def __init__(self, name, weight=0, version=None):
        self.name = name
        self.weight = weight
        self.version = version

    def css(self):
        return ""

    def js(self):
        return ""

    def script(self):
        return ""
