from flask import current_app

class RenderTemplateWidget:
    """
    WTForms widget that renders Jinja2 template
    """

    def __init__(self, template):
        """
        Constructor

        :param template:
            Template path
        """
        self.template = template

    def __call__(self, field, **kwargs):
        template = current_app.jinja_env.get_template(self.template)
        return template.render(kwargs)


class InlineFieldListWidget(RenderTemplateWidget):
    def __init__(self):
        super().__init__(
            "admin/model/inline_field_list.html"
        )


class InlineFormWidget(RenderTemplateWidget):
    def __init__(self):
        super().__init__("admin/model/inline_form.html")

    def __call__(self, field, **kwargs):
        kwargs.setdefault("form_opts", getattr(field, "form_opts", None))
        return super().__call__(field, **kwargs)

