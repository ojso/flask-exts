from flask import url_for
from .base_plugin import PluginBase


class XeditorPlugin(PluginBase):
    def __init__(self):
        super().__init__("xeditor")

    def css(self):
        return url_for(
            "_template.static", filename="vendor/vanilla-editor/css/bootstrap-editable.css"
        )

    def js(self):
        return url_for(
            "_template.static", filename="vendor/vanilla-editor/js/bootstrap-editable.min.js"
        )


