from os import urandom
from datetime import timedelta
from werkzeug.utils import cached_property
from wtforms.csrf.session import SessionCSRF
from flask import session
from flask import current_app


class SessionCSRF:
    """
    Session CSRF token generation and validation support.
    """

    csrf = True
    csrf_class = SessionCSRF
    _csrf_secret = urandom(24)

    @property
    def csrf_secret(self):
        secret = current_app.secret_key or self._csrf_secret
        if isinstance(secret, str):
            secret = secret.encode("utf-8")
        return secret

    @property
    def csrf_context(self):
        return session

    @cached_property
    def csrf_time_limit(self):
        return timedelta(minutes=30)
