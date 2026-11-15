import pytest
from flask import Flask, session
from werkzeug.middleware.proxy_fix import ProxyFix

from flask_exts.builtin_extensions.security_ext import SecurityExtension
from flask_exts.security.browser import (
    DEFAULT_SECURITY_HEADERS,
    configure_secure_cookies,
    validate_secure_cookie_config,
)


def _add_session_route(app):
    @app.get("/test-session")
    def test_session():
        session["marker"] = True
        return "ok"


def _make_app(**overrides):
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY="test_key",
        SQLALCHEMY_DATABASE_URI="sqlite://",
        JWT_SECRET_KEY="x" * 32,
    )
    app.config.update(overrides)
    return app


def test_security_headers_are_added_to_http_responses(app, client):
    response = client.get("/missing")

    for name, value in DEFAULT_SECURITY_HEADERS.items():
        assert response.headers[name] == value
    assert "Strict-Transport-Security" not in response.headers


def test_hsts_is_only_added_over_https(app, client):
    response = client.get("/missing", base_url="https://localhost")

    assert response.headers["Strict-Transport-Security"].startswith("max-age=")


def test_security_headers_can_be_disabled(app, client, monkeypatch):
    monkeypatch.setitem(app.config, "SECURITY_HEADERS_ENABLED", False)

    response = client.get("/missing")

    assert "X-Content-Type-Options" not in response.headers


def test_security_headers_can_be_overridden_or_removed(app, client, monkeypatch):
    monkeypatch.setitem(
        app.config,
        "SECURITY_HEADERS",
        {
            "X-Frame-Options": "DENY",
            "Content-Security-Policy": None,
            "X-Custom-Header": "custom",
        },
    )

    response = client.get("/missing")

    assert response.headers["X-Frame-Options"] == "DENY"
    assert "Content-Security-Policy" not in response.headers
    assert response.headers["X-Custom-Header"] == "custom"


def test_hsts_can_be_disabled(app, client, monkeypatch):
    monkeypatch.setitem(app.config, "SECURITY_HSTS_ENABLED", False)

    response = client.get("/missing", base_url="https://localhost")

    assert "Strict-Transport-Security" not in response.headers


def test_session_cookie_emits_secure_attributes_when_configured(
    app, client, monkeypatch
):
    _add_session_route(app)
    monkeypatch.setitem(app.config, "SESSION_COOKIE_SECURE", True)

    response = client.get("/test-session", base_url="https://localhost")

    cookie = response.headers["Set-Cookie"]
    assert "Secure" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie


def test_session_cookie_stays_usable_over_http(app, client):
    _add_session_route(app)

    response = client.get("/test-session")

    cookie = response.headers["Set-Cookie"]
    assert "Secure" not in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie


def test_secure_cookie_defaults_are_applied(app):
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
    assert app.config["REMEMBER_COOKIE_HTTPONLY"] is True
    assert app.config["REMEMBER_COOKIE_SAMESITE"] == "Lax"


def test_require_https_rejects_insecure_cookies():
    app = _make_app(SECURITY_REQUIRE_HTTPS=True)
    configure_secure_cookies(app)

    with pytest.raises(RuntimeError, match="SESSION_COOKIE_SECURE"):
        validate_secure_cookie_config(app)


def test_require_https_accepts_secure_cookies():
    app = _make_app(
        SECURITY_REQUIRE_HTTPS=True,
        SESSION_COOKIE_SECURE=True,
        REMEMBER_COOKIE_SECURE=True,
    )
    configure_secure_cookies(app)

    validate_secure_cookie_config(app)


def test_cookie_defaults_can_be_disabled():
    app = _make_app(SECURITY_COOKIE_DEFAULTS_ENABLED=False)

    configure_secure_cookies(app)

    assert app.config.get("SESSION_COOKIE_SAMESITE") is None
    assert app.config.get("REMEMBER_COOKIE_SAMESITE") is None


def test_explicit_samesite_none_is_emitted(app, client, monkeypatch):
    _add_session_route(app)
    monkeypatch.setitem(app.config, "SESSION_COOKIE_SAMESITE", "None")

    response = client.get("/test-session", base_url="https://localhost")

    assert "SameSite=None" in response.headers["Set-Cookie"]


def test_hsts_is_added_behind_a_trusted_proxy(app, client):
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)

    response = client.get(
        "/missing",
        environ_overrides={"HTTP_X_FORWARDED_PROTO": "https"},
    )

    assert "Strict-Transport-Security" in response.headers


def test_extension_initialization_accepts_valid_config():
    app = _make_app(SECURITY_HEADERS={"X-Custom-Header": "custom"})

    SecurityExtension().init_app(app)

    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"SECURITY_HEADERS": "X-Frame-Options: DENY"}, "must be a mapping"),
        ({"SECURITY_HEADERS": {"X-Frame-Options": 1}}, "must be a string"),
        ({"SECURITY_HEADERS": {"": "value"}}, "non-empty strings"),
        ({"SECURITY_HSTS": 5}, "SECURITY_HSTS"),
    ],
)
def test_extension_rejects_invalid_security_config(overrides, message):
    app = _make_app(**overrides)

    with pytest.raises(RuntimeError, match=message):
        SecurityExtension().init_app(app)
