from flask import url_for

from ..plugin_base import PluginBase


class AdminModalPlugin(PluginBase):
    def __init__(self):
        super().__init__("modal")

    def script(self):
        url = url_for("_template.static", filename="js/modal.js")
        return f'<script src="{url}"></script>'
