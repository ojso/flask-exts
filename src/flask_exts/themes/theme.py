import os.path as op
from flask import Blueprint
from .plugins.plugin_manager import PluginManager

LOCAL_VENDOR_URL = "/template/static/vendor"
ICON_SPRITE_URL = f"{LOCAL_VENDOR_URL}/bootstrap-icons/bootstrap-icons.svg"


class ThemeManager:
    icon_sprite_url = ICON_SPRITE_URL
    icon_size = "1em"
    btn_style = "primary"
    btn_size = "md"
    navbar_classes = "navbar-dark bg-dark"
    form_group_classes = "mb-3"
    form_inline_classes = "row row-cols-lg-auto g-3 align-items-center"
    swatch = "default"
    navbar_fluid: bool = True
    fluid: bool = False
    admin_base_template = "admin/master.html"
    title = {
        "view": "View",
        "edit": "Edit",
        "delete": "Remove",
        "new": "Create",
    }

    def __init__(self, name="default"):
        self.name = name
        self.plugin = PluginManager()

    def init_app(self, app):
        if app.config.get("THEME_NAME"):
            self.name = app.config.get("THEME_NAME")
        # print("Initializing ThemeManager with theme:", self.name)
        self.init_theme_blueprint(app)        
        self.plugin.init_app(app)

    def init_theme_blueprint(self, app):
        blueprint = Blueprint(
            "_template",
            __name__,
            url_prefix="/template",
            template_folder=op.join("./templates", self.name),
            static_folder="./static",
        )
        app.register_blueprint(blueprint)

    
