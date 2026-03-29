from flask import request
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.datastructures import ImmutableMultiDict

SUBMIT_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def is_submitted():
    """Check if current method is PUT or POST"""
    return request and request.method in SUBMIT_METHODS


def get_request_data():
    """If current method is PUT or POST,
    return concatenated `request.form` with `request.files` or `None` otherwise.
    """
    if is_submitted():
        if request.files:
            return CombinedMultiDict((request.files, request.form))
        elif request.form:
            return request.form
        elif request.is_json:
            return ImmutableMultiDict(request.get_json())
    return None
