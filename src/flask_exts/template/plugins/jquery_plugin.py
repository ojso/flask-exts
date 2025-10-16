from flask import url_for
from .base_plugin import BasePlugin


class jQueryPlugin(BasePlugin):
    def __init__(self):
        super().__init__("jquery")

    def js(self):
        return url_for("_template.static", filename="vendor/jquery/jquery.min.js")
