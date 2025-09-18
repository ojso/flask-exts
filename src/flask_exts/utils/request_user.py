from .jwt import jwt_decode
from .jwt import UnSupportedAuthType
from ..proxies import _userstore


def authorization_decoder(auth_str: str):
    """
    Authorization token decoder based on type. Current only support jwt.
    Args:
        auth_str: Authorization string should be in "<type> <token>" format
    Returns:
        decoded owner from token
    """
    type, token = auth_str.split()
    if type == "Bearer" and len(token.split(".")) == 3:
        payload = jwt_decode(token)
        return payload
    else:
        raise UnSupportedAuthType(
            "Authorization %s is not supported" % type,
            payload=auth_str,
        )


def load_user_from_request(request):
    # first, try to login using the api_key url arg
    # api_key = request.args.get('api_key')
    # if api_key:
    #     user = User.query.filter_by(api_key=api_key).first()
    #     if user:
    #         return user

    # next, try to login using Basic Auth
    # Basic is vulnerable, and not to use.
    # api_key = request.headers.get('Authorization')
    # if api_key:
    #     api_key = api_key.replace('Basic ', '', 1)
    #     try:
    #         api_key = base64.b64decode(api_key)
    #     except TypeError:
    #         pass
    #     user = User.query.filter_by(api_key=api_key).first()
    #     if user:
    #         return user

    # next, try to login using Bearer Jwt and load user

    if "Authorization" in request.headers:
        auth_str = request.headers.get("Authorization")
        payload = authorization_decoder(auth_str)
        if isinstance(payload, dict):
            if "id" in payload and payload["id"] is not None:
                user = _userstore.get_user_by_id(int(payload["id"]))
                if user:
                    return user
            identity = payload.get(_userstore.identity_name)
            if identity is not None:
                user = _userstore.get_user_by_identity(identity)
                if user:
                    return user
    # add other methods to get user

    # finally, return None if both methods did not login the user
    return None
