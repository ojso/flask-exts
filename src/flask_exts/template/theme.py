from markupsafe import Markup
from dataclasses import dataclass

LOCAL_VENDOR_URL = "/template/static/vendor"
ICON_SPRITE_URL = f"{LOCAL_VENDOR_URL}/bootstrap-icons/bootstrap-icons.svg"
ICON_FONT_CSS = f"{LOCAL_VENDOR_URL}/bootstrap-icons/font/bootstrap-icons.css"
JQUERY_JS_URL = f"{LOCAL_VENDOR_URL}/jquery/jquery.min.js"
BOOTSTRAP4_CSS_URL = f"{LOCAL_VENDOR_URL}/bootstrap4/bootstrap.min.css"
BOOTSTRAP4_JS_URL = f"{LOCAL_VENDOR_URL}/bootstrap4/bootstrap.bundle.min.js"
BOOTSTRAP5_CSS_URL = f"{LOCAL_VENDOR_URL}/bootstrap5/bootstrap.min.css"
BOOTSTRAP5_JS_URL = f"{LOCAL_VENDOR_URL}/bootstrap5/bootstrap.bundle.min.js"


@dataclass
class Bootstrap:
    version = 4
    btn_style = "primary"
    btn_size = "md"
    navbar_classes = "navbar-dark bg-dark"
    form_group_classes = "mb-3"
    form_inline_classes = "row row-cols-lg-auto g-3 align-items-center"
    swatch = "default"
    navbar_fluid: bool = True
    fluid: bool = False


@dataclass
class Title:
    view = "View"
    edit = "Edit"
    delete = "Remove"
    new = "Create"

class BootstrapTheme:
    admin_base_template: str = "admin/base.html"
    icon_sprite_url = ICON_SPRITE_URL
    icon_font_css = ICON_FONT_CSS
    icon_size = "1em"
    title = Title()

    def __init__(self,version=4):
        bootstrap = Bootstrap()
        bootstrap.version = version
        self.bootstrap = bootstrap

    def load_css(self):
        bootstrap_css_url = BOOTSTRAP4_CSS_URL if self.bootstrap.version < 5 else BOOTSTRAP5_CSS_URL
        css = (
            f'<link rel="stylesheet" href="{bootstrap_css_url}">'
            f'<link rel="stylesheet" href="{self.icon_font_css}">'
            )
        return Markup(css)

    def load_js(self):
        urls = []
        if self.bootstrap.version < 5:
            urls.append(f'<script src="{JQUERY_JS_URL}"></script>')
            urls.append(f'<script src="{BOOTSTRAP4_JS_URL}"></script>')
        else:
            urls.append(f'<script src="{BOOTSTRAP5_JS_URL}"></script>')

        return Markup("\n".join(urls))
