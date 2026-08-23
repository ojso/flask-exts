class InlineFieldListWidget:
    def __init__(self):
        self.template = "inline_field_list"

    def __call__(self, field, **kwargs):
        return "TODO:InlineFieldListWidget"


class InlineFormWidget:
    def __init__(self):
        self.template = "inline_form"

    def __call__(self, field, **kwargs):
        kwargs.setdefault("form_opts", getattr(field, "form_opts", None))
        return super().__call__(field, **kwargs)
