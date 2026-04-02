class PluginBase:
    _plugins = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._plugins[cls.__name__] = cls

    def __init__(self, name, weight=0):
        self.name = name
        self.weight = weight

    def css(self):
        return ""

    def js(self):
        return ""
