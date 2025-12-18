from flask import flash
from flask_babel import gettext


class FlaskMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def flash_form_errors(self, form, message):
        for field_name, errors in form.errors.items():
            errors = form[field_name].label.text + ": " + ", ".join(errors)
            flash(gettext(message, error=str(errors)), "error")
