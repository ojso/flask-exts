from functools import wraps
from flask import request, jsonify
from flask_login import current_user
from ..utils.request_user import UnSupportedAuthType
from ..proxies import current_authorizer


def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        uri = str(request.path)
        try:
            if current_user.is_authenticated:
                if current_authorizer.allow(current_user, uri, request.method):
                    return func(*args, **kwargs)
                return (jsonify({"message": "Forbidden"}), 403)
            else:
                # return current_app
                return (jsonify({"message": "Unauthorized"}), 401)

        except UnSupportedAuthType:
            return (jsonify({"message": "UnSupportedAuthType"}), 401)
        except Exception as e:
            return (jsonify({"message": str(e)}), 401)

    return wrapper
