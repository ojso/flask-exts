LOCAL_VENDOR_URL = "/template/static/vendor"
ICON_SPRITE_URL = f"{LOCAL_VENDOR_URL}/bootstrap-icons/bootstrap-icons.svg"


class Theme:
    form_group_class = "mb-3"
    icon_size = "1em"
    btn_style = "primary"
    btn_size = "md"
    form_inline_class = "row row-cols-lg-auto g-3 align-items-center"
    swatch = "default"
    fluid: bool = False
    icon_sprite_url = ICON_SPRITE_URL
    title = {
        "view": "View",
        "edit": "Edit",
        "delete": "Remove",
        "new": "Create",
    }

    def __init__(self, name="bootstrap5"):
        self.name = name

    def init_app(self, app):
        if app.config.get("THEME_NAME"):
            self.name = app.config.get("THEME_NAME")
