from flask import url_for
from .base_plugin import BasePlugin


class RedisCliPlugin(BasePlugin):
    def __init__(self):
        super().__init__("rediscli")

    def css(self):
        return url_for("_template.static", filename="css/rediscli.css")

    def js(self):
        return url_for("_template.static", filename="js/rediscli.js")
