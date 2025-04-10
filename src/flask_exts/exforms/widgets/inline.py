from .render_template import RenderTemplateWidget


class InlineFieldListWidget(RenderTemplateWidget):
    def __init__(self):
        super().__init__("widgets/inline_field_list.html")


class InlineFormWidget(RenderTemplateWidget):
    def __init__(self):
        super().__init__("widgets/inline_form.html")

    def __call__(self, field, **kwargs):
        kwargs.setdefault("form_opts", getattr(field, "form_opts", None))
        return super().__call__(field, **kwargs)
