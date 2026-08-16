from .base_form import BaseForm
from .meta import FlaskMeta


class FlaskForm(BaseForm):
    """Flask-WTF style form, includes CSRF token field."""

    Meta = FlaskMeta

    def render_csrf_token(self):
        """Render the form's csrf_token fields in one call."""
        if self.meta.csrf:
            csrf_field_name = self.meta.csrf_field_name
            csrf_field = self._fields[csrf_field_name]
            return csrf_field()
        else:
            return ""
