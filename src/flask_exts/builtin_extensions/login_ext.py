import datetime
import hmac

import jwt
from flask import current_app, has_request_context, session
from flask_login import LoginManager

from ..extension_core.base import Extension
from ..proxies import current_security, current_userstore

ALLOWED_JWT_ALGORITHMS = frozenset({"HS256", "HS384", "HS512"})
MIN_JWT_SECRET_KEY_BYTES = 32


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


def _as_bytes(value, name):
    if isinstance(value, str):
        return value.encode("utf-8")
    if isinstance(value, bytes):
        return value
    raise TypeError(f"{name} must be a string or bytes.")


def _jwt_secret_key(key=None):
    """Return a validated JWT signing key.

    The key is checked on first use rather than at application startup so
    deployments that never issue tokens are unaffected. A missing key, a short
    key, or a key identical to ``SECRET_KEY`` raises immediately instead of
    surfacing later as an opaque PyJWT error.
    """
    if key is None:
        key = current_app.config.get("JWT_SECRET_KEY")
    if key is None or key == "":
        raise RuntimeError("JWT_SECRET_KEY must be set before using JWT.")
    key_bytes = _as_bytes(key, "JWT_SECRET_KEY")
    if len(key_bytes) < MIN_JWT_SECRET_KEY_BYTES:
        raise RuntimeError(
            f"JWT_SECRET_KEY must be at least {MIN_JWT_SECRET_KEY_BYTES} bytes."
        )
    secret_key = current_app.config.get("SECRET_KEY")
    if secret_key is not None and key_bytes == _as_bytes(secret_key, "SECRET_KEY"):
        raise RuntimeError("JWT_SECRET_KEY must differ from SECRET_KEY.")
    return key_bytes


def _jwt_algorithm(algorithm=None):
    value = algorithm or current_app.config.get("JWT_HASH", "HS256")
    if value not in ALLOWED_JWT_ALGORITHMS:
        allowed = ", ".join(sorted(ALLOWED_JWT_ALGORITHMS))
        raise RuntimeError(
            f"Unsupported JWT algorithm {value!r}; allowed algorithms: {allowed}."
        )
    return value


def jwt_encode(payload, key=None, delta: int | None = None, algorithm=None):
    if delta is None:
        delta = current_app.config.get("JWT_ACCESS_TOKEN_MAX_AGE", 900)
    now = datetime.datetime.now(tz=datetime.UTC)
    token_payload = dict(payload)
    token_payload["iat"] = now
    token_payload["exp"] = now + datetime.timedelta(seconds=delta)
    token_payload["token_use"] = "access"
    token = jwt.encode(
        token_payload,
        _jwt_secret_key(key),
        algorithm=_jwt_algorithm(algorithm),
    )
    return token


def jwt_decode(token, key=None, algorithm=None):
    payload = jwt.decode(
        token,
        key=_jwt_secret_key(key),
        algorithms=[_jwt_algorithm(algorithm)],
        options={"require": ["exp", "token_use"]},
        leeway=current_app.config.get("JWT_LEEWAY", 0),
    )
    return payload


def password_fingerprint(user):
    """Return the keyed fingerprint of the user's current password hash.

    The fingerprint is deterministic (unlike the stored scrypt hash) because
    ``Blake2bHasher`` uses a key derived from ``SECRET_KEY``. It matches the
    fingerprint embedded in session ids by ``User.get_id``.
    """
    return current_security.hasher.hash(user.password or "")


def _normalize_amr(amr):
    """Normalize the ``amr`` argument to a list of unique method names.

    A bare string is treated as a single method; any other iterable must
    contain strings only. This prevents ``amr="otp"`` from silently becoming
    ``["o", "t", "p"]`` (the bug this helper was added for).
    """
    if amr is None:
        methods = []
    elif isinstance(amr, str):
        methods = [amr]
    else:
        try:
            methods = list(amr)
        except TypeError as error:
            raise TypeError(
                "amr must be a string or an iterable of strings."
            ) from error
    for method in methods:
        if not isinstance(method, str):
            raise TypeError("amr entries must be strings.")
    return list(dict.fromkeys(methods))


def jwt_encode_for_user(user, amr=None, delta=None):
    """Issue an access token bound to the user's current credentials.

    The token carries a ``pwd`` fingerprint and an ``amr`` claim so that
    ``load_user_from_request`` can reject tokens issued before a password
    change (SEC-08) and password-only tokens for TFA users (SEC-02).

    This helper only encodes the claims it is given; it cannot verify that a
    second factor actually happened. Callers must only pass ``"otp"`` after
    verifying a TOTP code or recovery code.

    Args:
        user: User instance to issue the token for.
        amr: Authentication methods already completed. A string is treated as
            one method. ``"pwd"`` is added automatically. When
            ``user.tfa_enabled`` is true, ``"otp"`` is required.
        delta: Token lifetime in seconds; defaults to
            ``JWT_ACCESS_TOKEN_MAX_AGE``.

    Raises:
        ValueError: If a TFA-enabled user is given without ``"otp"``.
        TypeError: If ``amr`` is not a string or an iterable of strings.
    """
    methods = _normalize_amr(amr)
    if "pwd" not in methods:
        methods.insert(0, "pwd")
    if getattr(user, "tfa_enabled", False) and "otp" not in methods:
        raise ValueError(
            "A token for a TFA-enabled user requires the 'otp' amr claim."
        )
    return jwt_encode(
        {"id": user.id, "pwd": password_fingerprint(user), "amr": methods},
        delta=delta,
    )


def _token_matches_user(payload, user):
    """Return whether a decoded token is still valid for ``user``."""
    if user is None or not user.is_active:
        return False
    claim = payload.get("pwd")
    if not isinstance(claim, str):
        return False
    if not hmac.compare_digest(claim, password_fingerprint(user)):
        return False
    if getattr(user, "tfa_enabled", False):
        amr = payload.get("amr")
        if not isinstance(amr, list) or "otp" not in amr:
            return False
    return True


def _parse_user_id(value):
    """Return a strict integer user id, or ``None`` for invalid input.

    ``bool`` is rejected explicitly because it is an ``int`` subclass, and
    floats are rejected instead of being truncated (``int(1.9) == 1``).
    Canonical decimal strings are accepted for compatibility with callers
    that encode ids as strings.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


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
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise InvalidAuthorizationError("Invalid authorization header.")
    try:
        payload = jwt_decode(parts[1])
    except (jwt.PyJWTError, TypeError, ValueError) as error:
        raise InvalidAuthorizationError("Invalid authorization token.") from error
    if payload.get("token_use") != "access":
        raise InvalidAuthorizationError("Invalid authorization token.")
    return payload


def load_user_from_request(request):
    if "Authorization" not in request.headers:
        return None
    authstr = request.headers.get("Authorization")
    try:
        payload = authorization_decoder(authstr)
    except InvalidAuthorizationError:
        return None
    if not isinstance(payload, dict):
        return None

    user = None
    if payload.get("id") is not None:
        user_id = _parse_user_id(payload["id"])
        if user_id is None:
            return None
        user = current_userstore.get_user_by_id(user_id)
    if user is None:
        identity = payload.get(current_userstore.identity_name)
        if identity is not None:
            user = current_userstore.get_user_by_identity(identity)

    if _token_matches_user(payload, user):
        return user
    # add other methods to get user

    # finally, return None if both methods did not login the user
    return None
