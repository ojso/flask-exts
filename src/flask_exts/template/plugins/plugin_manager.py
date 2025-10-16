class PluginManager:
    def __init__(self):
        self.plugins = {}
        self.enabled_plugins = []

    def register_plugin(self, plugin):
        self.plugins[plugin.name] = plugin

    def register_plugins(self, plugins):
        for plugin in plugins:
            self.register_plugin(plugin)

    def enable_plugin(self, names):
        if isinstance(names, str):
            names = [names]
        for name in names:
            if name not in self.enabled_plugins and name in self.plugins:
                self.enabled_plugins.append(name)
