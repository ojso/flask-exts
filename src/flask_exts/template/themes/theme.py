LOCAL_VENDOR_URL = "/template/static/vendor"
ICON_SPRITE_URL = f"{LOCAL_VENDOR_URL}/bootstrap-icons/bootstrap-icons.svg"


class Theme:
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
    admin_base_template = "admin/base.html"
    title = {
        "view": "View",
        "edit": "Edit",
        "delete": "Remove",
        "new": "Create",
    }

    def __init__(self):
        self.name = "default"
