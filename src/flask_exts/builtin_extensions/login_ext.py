import datetime

import jwt
from flask import current_app, has_request_context, session
from flask_login import LoginManager

from ..extension_core.base import Extension
from ..proxies import current_security, current_userstore


class InvalidAuthorizationError(ValueError):
    """Raised when an Authorization header is malformed or invalid."""


class LoginExtension(Extension):
    @property
    def name(self) -> str:
        return "login"

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
    try:
        raw_id, password_fingerprint = user_id.rsplit(":", 1)
        user = current_userstore.user_loader(int(raw_id))
    except (AttributeError, TypeError, ValueError):
        return None
    if user is None:
        return None
    if not user.is_active:
        # Revoke the disabled account's session and remember-me cookie.
        if has_request_context():
            session.pop("_user_id", None)
            session["_remember"] = "clear"
        return None
    if not current_security.hasher.verify(user.password or "", password_fingerprint):
        return None
    return user


def jwt_encode(payload, key=None, delta: int | None = None, algorithm=None):
    if delta is None:
        delta = current_app.config.get("JWT_ACCESS_TOKEN_MAX_AGE", 900)
    exp = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(seconds=delta)
    token_payload = dict(payload)
    token_payload["exp"] = exp
    token_payload["token_use"] = "access"
    token = jwt.encode(
        token_payload,
        key=key if key is not None else current_app.config.get("JWT_SECRET_KEY"),
        algorithm=algorithm or current_app.config.get("JWT_HASH", "HS256"),
    )
    return token


def jwt_decode(token, key=None, algorithm=None):
    payload = jwt.decode(
        token,
        key=key if key is not None else current_app.config.get("JWT_SECRET_KEY"),
        algorithms=[algorithm or current_app.config.get("JWT_HASH", "HS256")],
        options={"require": ["exp", "token_use"]},
    )
    return payload


def authorization_decoder(authstr: str):
    """Authorization token decoder based on type. Current only support jwt.

    Args:
        authstr: Authorization string should be in "<type> <token>" format
    Returns:
        decoded owner from token
    """
    if not isinstance(authstr, str):
        raise InvalidAuthorizationError("Invalid authorization header.")
    parts = authstr.split()
    if len(parts) != 2 or parts[0] != "Bearer":
        raise InvalidAuthorizationError("Invalid authorization header.")
    try:
        payload = jwt_decode(parts[1])
    except (jwt.PyJWTError, TypeError, ValueError) as error:
        raise InvalidAuthorizationError("Invalid authorization token.") from error
    if payload.get("token_use") != "access":
        raise InvalidAuthorizationError("Invalid authorization token.")
    return payload


def load_user_from_request(request):
    if "Authorization" in request.headers:
        authstr = request.headers.get("Authorization")
        try:
            payload = authorization_decoder(authstr)
        except InvalidAuthorizationError:
            return None
        if isinstance(payload, dict):
            if "id" in payload and payload["id"] is not None:
                try:
                    user_id = int(payload["id"])
                except (TypeError, ValueError):
                    return None
                user = current_userstore.get_user_by_id(user_id)
                if user is not None and user.is_active:
                    return user
            identity = payload.get(current_userstore.identity_name)
            if identity is not None:
                user = current_userstore.get_user_by_identity(identity)
                if user is not None and user.is_active:
                    return user
    # add other methods to get user

    # finally, return None if both methods did not login the user
    return None
