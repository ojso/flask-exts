from markupsafe import Markup
from dataclasses import dataclass


DEFAULT_BOOTSTRAP_VERSION = 4
LOCAL_VENDOR_URL = "/template/static/vendor"

ICON_SPRITE_URL = f"{LOCAL_VENDOR_URL}/bootstrap-icons/bootstrap-icons.svg"
JQUERY_JS_URL = f"{LOCAL_VENDOR_URL}/jquery/jquery.min.js"
BOOTSTRAP4_CSS_URL = f"{LOCAL_VENDOR_URL}/bootstrap4/bootstrap.min.css"
BOOTSTRAP4_JS_URL = f"{LOCAL_VENDOR_URL}/bootstrap4/bootstrap.bundle.min.js"
BOOTSTRAP5_CSS_URL = f"{LOCAL_VENDOR_URL}/bootstrap5/bootstrap.min.css"
BOOTSTRAP5_JS_URL = f"{LOCAL_VENDOR_URL}/bootstrap5/bootstrap.bundle.min.js"

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


@dataclass
class Bootstrap:
    icon_sprite_url = ICON_SPRITE_URL
    btn_style = "primary"
    btn_size = "md"
    icon_size = "1em"
    navbar_classes = "navbar-dark bg-dark"
    form_group_classes = "mb-3"
    form_inline_classes = "row row-cols-lg-auto g-3 align-items-center"

class Theme:
    name: str
    src: str = "local"

@dataclass
class Title:
    view = "View"
    edit = "Edit"
    delete = "Remove"
    new = "Create"

class DefaultTheme(Theme):
    name = "bootstrap"
    bootstrap_version = DEFAULT_BOOTSTRAP_VERSION
    swatch: str = "default"
    navbar_fluid: bool = True
    fluid: bool = False
    admin_base_template: str = "admin/base.html"
    bootstrap = Bootstrap()
    title = Title()

    def __init__(
        self,
        bootstrap_version=None,
        bootstrap_css_url=None,
        bootstrap_js_url=None,
        jquery_js_url=None,
    ):
        self.bootstrap_version = bootstrap_version or DEFAULT_BOOTSTRAP_VERSION
        self.bootstrap_css_url = bootstrap_css_url
        self.bootstrap_js_url = bootstrap_js_url
        self.jquery_js_url = jquery_js_url
        self.css_url = self._get_css_url()
        self.js_url = self._get_js_url()

    def load_css(self):
        return self.css_url

    def load_js(self):
        return self.js_url

    def _get_css_url(self):
        if self.bootstrap_css_url:
            bootstrap_css_url = (
                f'<link rel="stylesheet" href="{self.bootstrap_css_url}">'
            )
        elif self.bootstrap_version < 5:
            if self.src == "local":
                bootstrap_css_url = (
                    f'<link rel="stylesheet" href="{BOOTSTRAP4_CSS_URL}">'
                )
            else:
                bootstrap_css_url = cdns["bootstrap.min.css@4.6.2"]
        else:
            if self.src == "local":
                bootstrap_css_url = (
                    f'<link rel="stylesheet" href="{BOOTSTRAP5_CSS_URL}">'
                )
            else:
                bootstrap_css_url = cdns["bootstrap.min.css@5.3.3"]

        return Markup(bootstrap_css_url)

    def _get_js_url(self):
        if self.bootstrap_version < 5:
            if self.jquery_js_url:
                jquery_js_url = f'<script src="{self.jquery_js_url}"></script>'
            elif self.src == "local":
                jquery_js_url = f'<script src="{JQUERY_JS_URL}"></script>'
            else:
                jquery_js_url = cdns["jquery.slim.min.js@3.5.1"]
        else:
            jquery_js_url = ""

        if self.bootstrap_js_url:
            bootstrap_js_url = f'<script src="{self.bootstrap_js_url}"></script>'
        elif self.bootstrap_version < 5:
            if self.src == "local":
                bootstrap_js_url = f'<script src="{BOOTSTRAP4_JS_URL}"></script>'
            else:
                bootstrap_js_url = cdns["bootstrap.bundle.min.js@4.6.2"]
        else:
            if self.src == "local":
                bootstrap_js_url = f'<script src="{BOOTSTRAP5_JS_URL}"></script>'
            else:
                bootstrap_js_url = cdns["bootstrap.bundle.min.js@5.3.3"]

        return Markup(f"{jquery_js_url}\n{bootstrap_js_url}")
