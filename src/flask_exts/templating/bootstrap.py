from flask import current_app
from markupsafe import Markup

from ..utils import is_hidden_field_filter
from ..utils import get_table_titles

DEFAULT_BOOTSTRAP_VERSION = 4
CDN_JSDELIVR = "https://cdn.jsdelivr.net/npm"

sri = {
    "jquery.slim.min.js": {
        "3.5.1": "sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj"
    },
    "bootstrap.min.css": {
        "4.6.2": "sha384-xOolHFLEh07PJGoPkLv1IbcEPTNtaed2xpHsD9ESMhqIYd0nLMwNLD69Npy4HI+N",
        "5.3.3": "sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH",
    },
    "bootstrap.bundle.min.js": {
        "4.6.2": "sha384-Fy6S3B9q64WdZWQUiU+q4/2Lc9npb8tCaSX9FK7E8HnRr0Jz8D6OP9dO5Vg3Q9ct",
        "5.3.3": "sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz",
    },
}

cdns = {
    "jquery.slim.min.js@3.5.1": f'<script src="{CDN_JSDELIVR}/jquery@3.5.1/dist/jquery.slim.min.js" integrity="{sri["jquery.slim.min.js"]["3.5.1"]}" crossorigin="anonymous"></script>',
    "bootstrap.min.css@4.6.2": f'<link rel="stylesheet" href="{CDN_JSDELIVR}/bootstrap@4.6.2/dist/css/bootstrap.min.css" integrity="{sri["bootstrap.min.css"]["4.6.2"]}" crossorigin="anonymous">',
    "bootstrap.bundle.min.js@4.6.2": f'<script src="{CDN_JSDELIVR}/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js" integrity="{sri["bootstrap.bundle.min.js"]["4.6.2"]}" crossorigin="anonymous"></script>',
    "bootstrap.min.css@5.3.3": f'<link rel="stylesheet" href="{CDN_JSDELIVR}/bootstrap@5.3.3/dist/css/bootstrap.min.css" integrity="{sri["bootstrap.min.css"]["5.3.3"]}" crossorigin="anonymous">',
    "bootstrap.bundle.min.js@5.3.3": f'<script src="{CDN_JSDELIVR}/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="{sri["bootstrap.bundle.min.js"]["5.3.3"]}" crossorigin="anonymous"></script>',
}


class Bootstrap:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.extensions["templating"] = self

        if app.config.get("BOOTSTRAP_VERSION"):
            self.bootstrap_version = app.config["BOOTSTRAP_VERSION"]
        else:
            self.bootstrap_version = DEFAULT_BOOTSTRAP_VERSION

        app.jinja_env.globals["bootstrap"] = self
        app.jinja_env.globals["bootstrap_is_hidden_field"] = is_hidden_field_filter
        app.jinja_env.globals["get_table_titles"] = get_table_titles

        # default settings
        app.config.setdefault("BOOTSTRAP_SERVE_LOCAL", False)
        app.config.setdefault("BOOTSTRAP_BTN_STYLE", "primary")
        app.config.setdefault("BOOTSTRAP_BTN_SIZE", "md")
        app.config.setdefault("BOOTSTRAP_BOOTSWATCH_THEME", None)
        app.config.setdefault("BOOTSTRAP_ICON_SIZE", "1em")
        app.config.setdefault("BOOTSTRAP_ICON_COLOR", None)
        app.config.setdefault("BOOTSTRAP_MSG_CATEGORY", "primary")
        app.config.setdefault("BOOTSTRAP_TABLE_VIEW_TITLE", "View")
        app.config.setdefault("BOOTSTRAP_TABLE_EDIT_TITLE", "Edit")
        app.config.setdefault("BOOTSTRAP_TABLE_DELETE_TITLE", "Delete")
        app.config.setdefault("BOOTSTRAP_TABLE_NEW_TITLE", "New")
        app.config.setdefault(
            "BOOTSTRAP_FORM_GROUP_CLASSES", "mb-3"
        )  # Bootstrap 5 only
        app.config.setdefault(
            "BOOTSTRAP_FORM_INLINE_CLASSES",
            "row row-cols-lg-auto g-3 align-items-center",
        )  # Bootstrap 5 only

    def load_css(self):
        """Load Bootstrap's css resources with given version."""

        if current_app.config.get("BOOTSTRAP_CSS_URL"):
            bootstrap_css_url = f'<link rel="stylesheet" href="{current_app.config["BOOTSTRAP_CSS_URL"]}">'
        elif self.bootstrap_version == 5:
            bootstrap_css_url = cdns["bootstrap.min.css@5.3.3"]
        else:
            bootstrap_css_url = cdns["bootstrap.min.css@4.6.2"]
        return Markup(bootstrap_css_url)

    def load_js(self):
        """Load Bootstrap and related library's js resources with given version.
        :param version: The version of Bootstrap.
        """
        if current_app.config.get("JQUERY_JS_URL"):
            jquery_js_url = f'<script src="{current_app.config["JQUERY_JS_URL"]}"></script>'
        elif self.bootstrap_version == 4:
            jquery_js_url = cdns["jquery.slim.min.js@3.5.1"]
        else:
            jquery_js_url = ""

        if current_app.config.get("BOOTSTRAP_JS_URL"):
            bootstrap_js_url = f'<script src="{current_app.config["BOOTSTRAP_JS_URL"]}"></script>'
        elif self.bootstrap_version == 5:
            bootstrap_js_url = cdns["bootstrap.bundle.min.js@5.3.3"]
        else:
            bootstrap_js_url = cdns["bootstrap.bundle.min.js@4.6.2"]

        return Markup(f"{jquery_js_url}{bootstrap_js_url}")
