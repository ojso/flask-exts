from flask import url_for
from .base_plugin import PluginBase


class AdminListActionPlugin(PluginBase):
    def __init__(self):
        super().__init__("list_action")

    def js(self):
        return url_for("_template.static", filename="js/list_action.js")
