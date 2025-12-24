import jwt
import datetime
from flask import current_app


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
