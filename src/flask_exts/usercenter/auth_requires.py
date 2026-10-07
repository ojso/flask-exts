from functools import wraps

from flask import jsonify, request
from flask_login import current_user

from ..proxies import current_security


def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        uri = str(request.path)
        if not current_user.is_authenticated:
            return jsonify({"message": "Unauthorized"}), 401
        if current_security.authorize_allow(resource=uri, method=request.method):
            return func(*args, **kwargs)
        return jsonify({"message": "Forbidden"}), 403

    return wrapper


def needs_required(**needs):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"message": "Unauthorized"}), 401
            if current_security.authorize_allow(**needs):
                return func(*args, **kwargs)
            return jsonify({"message": "Forbidden"}), 403

        return wrapper

    return decorator
