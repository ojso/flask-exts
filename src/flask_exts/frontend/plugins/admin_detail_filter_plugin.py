from flask import url_for

from ..plugin_base import PluginBase


class AdminDetailFilterPlugin(PluginBase):
    def __init__(self):
        super().__init__("detail_filter")

    def script(self):
        url = url_for("_template.static", filename="js/detail_filter.js")
        return f'<script src="{url}"></script>'
