from werkzeug.datastructures import CombinedMultiDict
from werkzeug.datastructures import ImmutableMultiDict
from wtforms.validators import DataRequired, InputRequired
from flask import request
from flask import flash
from .validators.field_list import FieldListInputRequired
from .babel import gettext

SUBMIT_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def is_form_submitted():
    """Check if current method is PUT or POST"""
    return request and request.method in SUBMIT_METHODS


def get_form_data():
    """If current method is PUT or POST,
    return concatenated `request.form` with `request.files` or `None` otherwise.
    """
    if is_form_submitted():
        if request.files:
            return CombinedMultiDict((request.files, request.form))
        elif request.form:
            return request.form
        elif request.is_json:
            return ImmutableMultiDict(request.get_json())
    return None


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


class FormOpts(object):
    __slots__ = ["widget_args", "form_rules"]

    def __init__(self, widget_args=None, form_rules=None):
        self.widget_args = widget_args or {}
        self.form_rules = form_rules
