from flask import current_app
from ...babel import _gettext,_ngettext
from ... import helpers as h


class RenderTemplateWidget:
    """WTForms widget that renders Jinja2 template"""

    def __init__(self, template):
        """Constructor

        :param template:
            Template path
        """
        self.template = template

    def __call__(self, field, **kwargs):
        kwargs.update(
            {
                "field": field,
                "_gettext": _gettext,
                "_ngettext": _ngettext,
                "h": h,
            }
        )

        template = current_app.jinja_env.get_template(self.template)
        return template.render(kwargs)
