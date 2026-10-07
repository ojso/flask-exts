from dataclasses import dataclass


@dataclass
class Theme:
    form_group_class = "mb-3"
    icon_size = "1em"
    btn_style = "primary"
    btn_size = "md"
    swatch = "default"
    fluid = False
    title = {
        "view": "View",
        "edit": "Edit",
        "delete": "Remove",
        "new": "Create",
    }
