from functools import wraps
from flask import request, jsonify
from flask_login import current_user
from .request_user import UnSupportedAuthType
from ..proxies import _security


def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        uri = str(request.path)
        try:
            if current_user.is_authenticated:
                if _security.authorize_allow(resource=uri, method=request.method):
                    return func(*args, **kwargs)
                return (jsonify({"message": "Forbidden"}), 403)
            else:
                return (jsonify({"message": "Unauthorized"}), 401)

        except UnSupportedAuthType:
            return (jsonify({"message": "UnSupportedAuthType"}), 401)
        except Exception as e:
            return (jsonify({"message": str(e)}), 401)

    return wrapper


def needs_required(**needs):
    def auth_required(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                if current_user.is_authenticated:
                    if _security.authorize_allow(**needs):
                        return func(*args, **kwargs)
                    return (jsonify({"message": "Forbidden"}), 403)
                else:
                    return (jsonify({"message": "Unauthorized"}), 401)

            except UnSupportedAuthType:
                return (jsonify({"message": "UnSupportedAuthType"}), 401)
            except Exception as e:
                return (jsonify({"message": str(e)}), 401)

        return wrapper

    return auth_required
