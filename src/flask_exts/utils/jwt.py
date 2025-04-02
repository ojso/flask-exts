import jwt
import datetime
from flask import current_app


class UnSupportedAuthType(Exception):
    status_code = 501

    def __init__(self, message, payload=None):
        Exception.__init__(self, message)
        self.payload = payload


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
