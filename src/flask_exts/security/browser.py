from collections.abc import Mapping

from flask import current_app, request

DEFAULT_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "SAMEORIGIN",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Content-Security-Policy": "frame-ancestors 'self'",
}

DEFAULT_HSTS = "max-age=31536000; includeSubDomains"


def configure_secure_cookies(app):
    """Apply safe cookie defaults without forcing HTTPS-only cookies.

    Flask already defaults ``HTTPONLY`` to ``True``, but ``SAMESITE`` is
    ``None``. Applications that need the raw Flask behavior (for example,
    cross-site cookies that must omit ``SameSite``) can set
    ``SECURITY_COOKIE_DEFAULTS_ENABLED = False``.

    ``None`` is treated as "not configured" because Flask also uses it as its
    own default, so it cannot express "explicitly no SameSite". To emit
    ``SameSite=None``, set the string ``"None"`` on the ``*_COOKIE_SAMESITE``
    settings; browsers reject it unless the cookie is also ``Secure``.
    """
    if not app.config.get("SECURITY_COOKIE_DEFAULTS_ENABLED", True):
        return
    if app.config.get("SESSION_COOKIE_HTTPONLY") is None:
        app.config["SESSION_COOKIE_HTTPONLY"] = True
    if app.config.get("SESSION_COOKIE_SAMESITE") is None:
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    if app.config.get("REMEMBER_COOKIE_HTTPONLY") is None:
        app.config["REMEMBER_COOKIE_HTTPONLY"] = True
    if app.config.get("REMEMBER_COOKIE_SAMESITE") is None:
        app.config["REMEMBER_COOKIE_SAMESITE"] = "Lax"


def validate_security_config(app):
    """Validate security header settings before they reach a response.

    Rejecting bad values here turns a per-request ``TypeError`` from the
    ``after_request`` hook into an actionable startup error.
    """
    headers = app.config.get("SECURITY_HEADERS")
    if headers is not None:
        if not isinstance(headers, Mapping):
            raise RuntimeError(
                "SECURITY_HEADERS must be a mapping of header names to values."
            )
        for name, value in headers.items():
            if not isinstance(name, str) or not name:
                raise RuntimeError("SECURITY_HEADERS keys must be non-empty strings.")
            if value is not None and not isinstance(value, str):
                raise RuntimeError(
                    f"SECURITY_HEADERS[{name!r}] must be a string or None."
                )

    hsts = app.config.get("SECURITY_HSTS")
    if hsts is not None and not isinstance(hsts, str):
        raise RuntimeError("SECURITY_HSTS must be a string or None.")


def validate_secure_cookie_config(app):
    """Fail fast when HTTPS is required but cookies are not marked Secure."""
    if not app.config.get("SECURITY_REQUIRE_HTTPS", False):
        return
    insecure = [
        name
        for name in ("SESSION_COOKIE_SECURE", "REMEMBER_COOKIE_SECURE")
        if app.config.get(name) is not True
    ]
    if insecure:
        names = ", ".join(insecure)
        raise RuntimeError(
            "SECURITY_REQUIRE_HTTPS is enabled but these settings are not "
            f"True: {names}."
        )


def _security_headers():
    headers = dict(DEFAULT_SECURITY_HEADERS)
    overrides = current_app.config.get("SECURITY_HEADERS") or {}
    headers.update(overrides)
    return headers


def add_security_headers(response):
    """Attach the configured security headers to an outgoing response.

    ``Strict-Transport-Security`` is only emitted when ``request.is_secure``
    is true. Behind a TLS-terminating proxy that means the application must
    install ``werkzeug.middleware.proxy_fix.ProxyFix`` (and trust only known
    proxies); otherwise HTTPS requests look like plain HTTP and HSTS is
    silently skipped.
    """
    if not current_app.config.get("SECURITY_HEADERS_ENABLED", True):
        return response

    for name, value in _security_headers().items():
        if value is not None:
            response.headers.setdefault(name, value)

    if current_app.config.get("SECURITY_HSTS_ENABLED", True) and request.is_secure:
        hsts = current_app.config.get("SECURITY_HSTS", DEFAULT_HSTS)
        if hsts:
            response.headers.setdefault("Strict-Transport-Security", hsts)

    return response


def install_security_headers(app):
    """Register the response hook once per application."""
    if app.extensions.get("flask_exts_security_headers"):
        return
    app.extensions["flask_exts_security_headers"] = True
    app.after_request(add_security_headers)
