from markupsafe import Markup


class InlineModelWidget:
    input_type = "inline"

    def __call__(self, field, **kwargs):
        return Markup("")
