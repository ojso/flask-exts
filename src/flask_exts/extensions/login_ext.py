import jwt
import datetime
from flask import current_app
from flask_login import LoginManager
from ..extension_core.base import Extension
from ..proxies import current_userstore



class LoginExtension(Extension):
    @property
    def name(self) -> str:
        return "login"

    @property
    def priority(self) -> int:
        return 10

    def init_app(self, app):
        if hasattr(app, "login_manager"):
            raise RuntimeError("FlaskLogin instance has already been registered.")

        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = "user.login"
        # login_manager.login_message = "Please login in"
        login_manager.user_loader(user_loader)
        login_manager.request_loader(load_user_from_request)


def user_loader(user_id):
    return current_userstore.user_loader(int(user_id))


def jwt_encode(payload, key=None, delta: int = None, algorithm=None):
    if delta is not None:
        exp = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
            seconds=delta
        )
        payload |= {"exp": exp}
    token = jwt.encode(
        payload,
        key=key or current_app.config.get("JWT_SECRET_KEY"),
        algorithm=algorithm or current_app.config.get("JWT_HASH", "HS256"),
    )
    return token


def jwt_decode(token, key=None, algorithm=None):
    payload = jwt.decode(
        token,
        key=key or current_app.config.get("JWT_SECRET_KEY"),
        algorithms=[algorithm or current_app.config.get("JWT_HASH", "HS256")],
    )
    return payload


def authorization_decoder(authstr: str):
    """
    Authorization token decoder based on type. Current only support jwt.
    Args:
        authstr: Authorization string should be in "<type> <token>" format
    Returns:
        decoded owner from token
    """
    type, token = authstr.split()
    if type == "Bearer" and len(token.split(".")) == 3:
        payload = jwt_decode(token)
        return payload
    else:
        raise Exception(f"Authorization {type} is not supported")


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
        authstr = request.headers.get("Authorization")
        payload = authorization_decoder(authstr)
        if isinstance(payload, dict):
            if "id" in payload and payload["id"] is not None:
                user = current_userstore.get_user_by_id(int(payload["id"]))
                if user:
                    return user
            identity = payload.get(current_userstore.identity_name)
            if identity is not None:
                user = current_userstore.get_user_by_identity(identity)
                if user:
                    return user
    # add other methods to get user

    # finally, return None if both methods did not login the user
    return None
