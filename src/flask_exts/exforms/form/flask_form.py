from .base_form import BaseForm
from .meta import FlaskMeta


class FlaskForm(BaseForm):
    """Flask-specific subclass of WTForms :class:`~wtforms.form.Form`.

    If ``formdata`` is not specified, this will use :attr:`flask.request.form`
    and :attr:`flask.request.files`.  Explicitly pass ``formdata=None`` to
    prevent this.
    """

    Meta = FlaskMeta

    def render_csrf_token(self):
        """Render the form's csrf_token fields in one call."""
        if self.meta.csrf:
            csrf_field_name = self.meta.csrf_field_name
            csrf_field = self._fields[csrf_field_name]
            return csrf_field()
        else:
            return ""
