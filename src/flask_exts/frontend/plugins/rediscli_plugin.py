from flask import url_for

from ..plugin_base import PluginBase


class RedisCliPlugin(PluginBase):
    def __init__(self):
        super().__init__("rediscli")

    def style(self):
        url = url_for("_template.static", filename="css/rediscli.css")
        return f'<link rel="stylesheet" href="{url}">'

    def script(self):
        url = url_for("_template.static", filename="js/rediscli.js")
        return f'<script src="{url}"></script>'
