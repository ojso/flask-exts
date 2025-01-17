from flask import request
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.datastructures import ImmutableMultiDict


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


def validate_form_on_submit(form):
    """
    If current method is PUT or POST, validate form and return validation status.
    """
    return is_form_submitted() and form.validate()
