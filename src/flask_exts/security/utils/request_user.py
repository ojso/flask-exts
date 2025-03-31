from base64 import b64decode
from flask import current_app
from .jwtcode import jwt_decode
from ..proxies import current_usercenter

AUTH_HEADER_NAME = "Authorization"

class UnSupportedAuthType(Exception):
    status_code = 501

    def __init__(self, message, status_code=None, payload=None, errors=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        self.errors = errors

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        if self.errors is not None:
            rv["errors"] = self.errors
        return rv


def authorization_decoder(auth_str: str):
    """
    Authorization token decoder based on type. This will decode the token and
    only return the owner
    Args:
        auth_str: Authorization string should be in "<type> <token>" format
    Returns:
        decoded owner from token
    """
    type, token = auth_str.split()

    if type == "Basic":
        """Basic format <user>:<password> return only the user"""
        return b64decode(token).decode().split(":")[0]
    elif type == "Bearer" and len(token.split(".")) == 3:
        """return identity, depends on JWT"""
        payload = jwt_decode(
            token,
            current_app.config.get("JWT_SECRET_KEY"),
            algorithm=current_app.config.get("JWT_HASH"),
        )
        return payload
    else:
        raise UnSupportedAuthType("%s Authorization is not supported" % type)

def load_user_from_request(request):
    if AUTH_HEADER_NAME in request.headers:
        auth_str = request.headers.get(AUTH_HEADER_NAME)
        payload = authorization_decoder(auth_str)
        if isinstance(payload,dict):
            if "identity" in payload:
                return payload["identity"]
            elif "id" in payload and payload["id"] is not None:
                user = current_usercenter.get_user_by_id(int(payload["id"]))
                return user
            elif "uniquifier" in payload and payload["uniquifier"] is not None:
                user = current_usercenter.get_user_by_uniquifier(payload["uniquifier"])            
                return user
            else:
                return payload
        else:
            return payload 

    # TODO: add other methods to get user
    # return None if no other methods to get user
    return None