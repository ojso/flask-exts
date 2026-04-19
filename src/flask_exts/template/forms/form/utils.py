from flask import request

SUBMIT_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def is_submitted():
    """Check if current method is PUT or POST"""
    return request and request.method in SUBMIT_METHODS
