from wtforms import Form
from flask import flash
from flask_babel import gettext
from .utils import is_form_submitted

class BaseForm(Form):
    """Flask-specific subclass of WTForms :class:`~wtforms.form.Form`.

    If ``formdata`` is not specified, this will use :attr:`flask.request.form`
    and :attr:`flask.request.files`.  Explicitly pass ``formdata=None`` to
    prevent this.
    """

    def __init__(self, formdata=None, **kwargs):
        super().__init__(formdata=formdata, **kwargs)

    def validate_on_submit(self):
        return is_form_submitted() and self.validate()

    def flash_errors(self, message):
        for field_name, errors in self.errors.items():
            err = self[field_name].label.text + ": " + ", ".join(errors)
            flash(gettext(message, error=str(err)), "error")