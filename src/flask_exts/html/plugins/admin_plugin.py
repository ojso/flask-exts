from flask import url_for
from ..plugin_base import PluginBase


class AdminPlugin(PluginBase):
    def __init__(self):
        super().__init__("admin")

    def style(self):
        url = url_for("_template.static", filename="css/admin.css")
        return f'<link rel="stylesheet" href="{url}">'
