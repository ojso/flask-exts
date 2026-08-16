from flask import url_for
from .base_plugin import PluginBase


class AdminAdminPlugin(PluginBase):
    def __init__(self):
        super().__init__("admin")

    def css(self):
        return url_for("_template.static", filename="css/admin.css")
