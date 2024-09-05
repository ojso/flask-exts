from .meta import FlaskMeta
from .base_form import BaseForm
from ...utils import is_form_submitted


class FlaskForm(BaseForm):
    """Flask-specific subclass of WTForms :class:`~wtforms.form.Form`.

    If ``formdata`` is not specified, this will use :attr:`flask.request.form`
    and :attr:`flask.request.files`.  Explicitly pass ``formdata=None`` to
    prevent this.
    """

    Meta = FlaskMeta

    def __init__(self, formdata=None, **kwargs):
        super().__init__(formdata=formdata, **kwargs)

    def validate_on_submit(self, extra_validators=None):
        """Call :meth:`validate` only if the form is submitted.
        This is a shortcut for ``form.is_submitted() and form.validate()``.
        """
        return is_form_submitted() and self.validate(extra_validators=extra_validators)

    def render_csrf_token(self):
        """Render the form's csrf_token fields in one call."""
        if self.meta.csrf:
            csrf_field_name = self.meta.csrf_field_name
            csrf_field = self._fields[csrf_field_name]
            return csrf_field()
        else:
            return ""
