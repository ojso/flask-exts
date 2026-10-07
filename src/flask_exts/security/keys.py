import hmac


def derive_key(secret_key: str | bytes | None, purpose: str) -> bytes:
    """Derive a purpose-specific key from Flask's application secret."""
    if secret_key is None:
        raise RuntimeError("Flask SECRET_KEY must be set before using security keys.")
    if isinstance(secret_key, str):
        secret_key = secret_key.encode("utf-8")
    elif not isinstance(secret_key, bytes):
        raise TypeError("Flask SECRET_KEY must be a string or bytes.")
    if not secret_key:
        raise ValueError("Flask SECRET_KEY must not be empty.")

    context = f"flask-exts:key-derivation:v1:{purpose}".encode("ascii")
    return hmac.digest(secret_key, context, "sha256")


def csrf_key(secret_key: str | bytes | None, config) -> str | bytes | None:
    """Return the configured CSRF key or derive a dedicated key."""
    if "CSRF_SECRET_KEY" in config:
        return config["CSRF_SECRET_KEY"]
    return derive_key(secret_key, "csrf")
