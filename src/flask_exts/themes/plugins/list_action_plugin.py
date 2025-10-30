from flask import url_for
from .base_plugin import BasePlugin


class ListActionPlugin(BasePlugin):
    def __init__(self):
        super().__init__("model_action")

    def js(self):
        return url_for("_template.static", filename="js/model_action.js")
