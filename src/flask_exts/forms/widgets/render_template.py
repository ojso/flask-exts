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
        kwargs.update(
            {
                "field": field,
            }
        )
        template = current_app.jinja_env.get_template(self.template)
        return template.render(kwargs)
