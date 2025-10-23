from flask import url_for
from .base_plugin import BasePlugin


class SphinxCopyButtonPlugin(BasePlugin):
    def __init__(self):
        super().__init__("sphinx_copybutton")

    def css(self):
        return url_for("_template.static", filename="vendor/sphinx_copybutton/sphinx_copybutton.css")

    def js(self):
        return url_for("_template.static", filename="vendor/sphinx_copybutton/sphinx_copybutton.js")
