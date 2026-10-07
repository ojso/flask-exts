from flask import url_for

from ..plugin_base import PluginBase


class SphinxCopyButtonPlugin(PluginBase):
    def __init__(self):
        super().__init__("sphinx_copybutton")

    def style(self):
        url = url_for(
            "_template.static",
            filename="vendor/sphinx_copybutton/sphinx_copybutton.css",
        )
        return f'<link rel="stylesheet" href="{url}">'

    def script(self):
        url = url_for(
            "_template.static", filename="vendor/sphinx_copybutton/sphinx_copybutton.js"
        )
        return f'<script src="{url}"></script>'
