class TokenActionError(Exception):
    """Base class for expected token-action failures."""

    status = "invalid_token"


class ExpiredTokenError(TokenActionError):
    status = "expired"


class InvalidTokenError(TokenActionError):
    status = "invalid_token"


class TokenUserNotFoundError(TokenActionError):
    status = "no_user"


class EmailNotVerifiedError(TokenActionError):
    status = "email_not_verified"


class MissingPasswordError(TokenActionError):
    status = "missing_password"
