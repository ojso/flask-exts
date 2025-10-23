from markupsafe import Markup
from .copybutton_plugin import CopyButtonPlugin
from .jquery_plugin import jQueryPlugin
from .bootstrap4_plugin import Bootstrap4Plugin
from .qrcode_plugin import QRCodePlugin
from .rediscli_plugin import RedisCliPlugin


class PluginManager:
    def __init__(self):
        self.registered_plugins = {}
        self.enabled_plugins = []

    def register_plugin(self, plugin):
        self.registered_plugins[plugin.name] = plugin

    def enable_plugin(self, names):
        if isinstance(names, str):
            names = [names]
        for name in names:
            if name not in self.enabled_plugins and name in self.registered_plugins:
                self.enabled_plugins.append(name)

    def init_app(self, app):
        # Register plugins
        [
            self.register_plugin(p)
            for p in (
                jQueryPlugin(),
                Bootstrap4Plugin(),
                QRCodePlugin(),
                CopyButtonPlugin(),
                RedisCliPlugin(),
            )
        ]
        # print("registered plugins:", [k for k in self.registered_plugins])

    def load_css(self):
        css_links = [
            f'<link rel="stylesheet" href="{css}">'
            for name in self.enabled_plugins
            if (plugin := self.registered_plugins.get(name)) and (css := plugin.css())
        ]
        css = "\n".join(css_links)
        return Markup(css)

    def load_js(self):
        js_links = [
            f'<script src="{js}"></script>'
            for name in self.enabled_plugins
            if (plugin := self.registered_plugins.get(name)) and (js := plugin.js())
        ]
        js = "\n".join(js_links)
        return Markup(js)

