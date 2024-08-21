import hashlib
import hmac
import os
from flask import current_app
from flask import g
from flask import session
from itsdangerous import BadData
from itsdangerous import SignatureExpired
from itsdangerous import URLSafeTimedSerializer
from wtforms import ValidationError

CONFIG_CSRF_SECRET_KEY = "CSRF_SECRET_KEY"
CONFIG_CSRF_FIELD_NAME = "CSRF_FIELD_NAME"
CONFIG_CSRF_TIME_LIMIT = "CSRF_TIME_LIMIT"
DEFAULT_CSRF_FIELD_NAME = "csrf_token"
DEFAULT_CSRF_TIME_LIMIT = 3600


def generate_csrf(secret_key=None, token_key=None):
    """Generate a CSRF token. The token is cached for a request, so multiple calls to this function will generate the same token.

    During testing, it might be useful to access the signed token in ``g.csrf_token`` and the raw token in ``session['csrf_token']``.

    :param secret_key: Used to securely sign the token. Default is ``CSRF_SECRET_KEY`` or ``SECRET_KEY``.
    :param token_key: Key where token is stored in session for comparison. Default is ``CSRF_FIELD_NAME`` or ``'csrf_token'``.
    """
    if secret_key is None:
        secret_key = _get_config(
            CONFIG_CSRF_SECRET_KEY,
            current_app.secret_key,
            message="A secret key is required to use CSRF.",
        )

    field_name = (
        token_key
        if token_key is not None
        else _get_config(
            CONFIG_CSRF_FIELD_NAME,
            DEFAULT_CSRF_FIELD_NAME,
            message="A field name is required to use CSRF.",
        )
    )

    if field_name not in g:
        s = URLSafeTimedSerializer(secret_key, salt="csrf-token")

        if field_name not in session:
            session[field_name] = hashlib.sha1(os.urandom(64)).hexdigest()

        try:
            token = s.dumps(session[field_name])
        except TypeError:
            session[field_name] = hashlib.sha1(os.urandom(64)).hexdigest()
            token = s.dumps(session[field_name])

        setattr(g, field_name, token)

    return g.get(field_name)


def validate_csrf(data, secret_key=None, token_key=None, time_limit=None):
    """Check if the given data is a valid CSRF token. This compares the given signed token to the one stored in the session.

    :param data: The signed CSRF token to be checked.
    :param secret_key: Used to securely sign the token. Default is ``CSRF_SECRET_KEY`` or ``SECRET_KEY``.
    :param time_limit: Number of seconds that the token is valid. Default is ``CSRF_TIME_LIMIT`` or 3600 seconds (60 minutes).
    :param token_key: Key where token is stored in session for comparison. Default is ``CSRF_FIELD_NAME`` or ``'csrf_token'``.

    :raises ValidationError: Contains the reason that validation failed.
    """

    if secret_key is None:
        secret_key = _get_config(
            CONFIG_CSRF_SECRET_KEY,
            current_app.secret_key,
            message="A secret key is required to use CSRF.",
        )

    field_name = (
        token_key
        if token_key is not None
        else _get_config(
            CONFIG_CSRF_FIELD_NAME,
            DEFAULT_CSRF_FIELD_NAME,
            message="A field name is required to use CSRF.",
        )
    )

    if time_limit is None:
        time_limit = _get_config(
            CONFIG_CSRF_TIME_LIMIT, DEFAULT_CSRF_TIME_LIMIT, required=False
        )

    if not data:
        raise ValidationError("The CSRF token is missing.")

    if field_name not in session:
        raise ValidationError("The CSRF session token is missing.")

    s = URLSafeTimedSerializer(secret_key, salt="csrf-token")

    try:
        token = s.loads(data, max_age=time_limit)
    except SignatureExpired as e:
        raise ValidationError("The CSRF token has expired.") from e
    except BadData as e:
        raise ValidationError("The CSRF token is invalid.") from e

    if not hmac.compare_digest(session[field_name], token):
        raise ValidationError("The CSRF tokens do not match.")


def _get_config(flask_config_name, default=None, required=True, message=None):
    """Find config value based on provided value, Flask config, and default value.

    :param config_name: Flask ``config`` key
    :param default: default value
    :param required: whether the value must not be ``None``
    :param message: error message if required config is not found
    :raises KeyError: if required config is not found
    """

    value = current_app.config.get(flask_config_name, default)

    if required and value is None:
        if message is None:
            message = "%s is not configured in app.config." % flask_config_name
        raise RuntimeError(message)

    return value
