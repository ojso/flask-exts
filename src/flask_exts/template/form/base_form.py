from wtforms import Form
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
