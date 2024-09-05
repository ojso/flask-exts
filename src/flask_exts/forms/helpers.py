from wtforms.validators import DataRequired, InputRequired
from flask import flash
from .validators.field_list import FieldListInputRequired
from ..babel import gettext

def is_field_error(errors):
    """Check if wtforms field has error without checking its children.

    :param errors:
        Errors list.
    """
    if isinstance(errors, (list, tuple)):
        for e in errors:
            if isinstance(e, str):
                return True

    return False


def flash_errors(form, message):
    for field_name, errors in form.errors.items():
        errors = form[field_name].label.text + ": " + ", ".join(errors)
        flash(gettext(message, error=str(errors)), "error")


def is_required_form_field(field):
    """
    Check if form field has `DataRequired`, `InputRequired`, or
    `FieldListInputRequired` validators.

    :param field:
        WTForms field to check
    """
    for validator in field.validators:
        if isinstance(validator, (DataRequired, InputRequired, FieldListInputRequired)):
            return True
    return False
