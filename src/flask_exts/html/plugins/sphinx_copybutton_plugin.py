from flask import url_for
from ..plugin_base import PluginBase


class SphinxCopyButtonPlugin(PluginBase):
    def __init__(self):
        super().__init__("sphinx_copybutton")

    def css(self):
        return url_for("_template.static", filename="vendor/sphinx_copybutton/sphinx_copybutton.css")

    def js(self):
        return url_for("_template.static", filename="vendor/sphinx_copybutton/sphinx_copybutton.js")
