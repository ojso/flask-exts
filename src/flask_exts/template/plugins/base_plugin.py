class PluginBase:
    _plugins = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._plugins[cls.__name__] = cls

    def __init__(self, name):
        self.name = name

    def css(self):
        return ""

    def js(self):
        return ""
