from flask import request
from flask import flash
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.datastructures import ImmutableMultiDict
from wtforms import HiddenField
from wtforms.validators import DataRequired, InputRequired
from flask_babel import gettext

SUBMIT_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def is_hidden_field(field):
    return isinstance(field, HiddenField)


def is_form_submitted():
    """Check if current method is PUT or POST"""
    return request and request.method in SUBMIT_METHODS

def validate_form_on_submit(form):
    """
        If current method is PUT or POST, validate form and return validation status.
    """
    return is_form_submitted() and form.validate()


def get_formdata():
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


def get_table_titles(data, primary_key, primary_key_title):
    """Detect and build the table titles tuple from ORM object, currently only support SQLAlchemy."""
    if not data:
        return []
    titles = []
    for k in data[0].__table__.columns.keys():
        if not k.startswith("_"):
            titles.append((k, k.replace("_", " ").title()))
    titles[0] = (primary_key, primary_key_title)
    return titles


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

def is_required_form_field(field):
    """
        Check if form field has `DataRequired`, `InputRequired`

        :param field:
            WTForms field to check
    """
    for validator in field.validators:
        if isinstance(validator, (DataRequired, InputRequired)):
            return True
    return False

def flash_errors(form, message):
    for field_name, errors in form.errors.items():
        errors = form[field_name].label.text + ": " + ", ".join(errors)
        flash(gettext(message, error=str(errors)), "error")
