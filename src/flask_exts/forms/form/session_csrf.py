from datetime import timedelta

from flask import current_app, session
from wtforms.csrf.session import SessionCSRF

from ...security.keys import derive_key


class SessionCSRF:
    """
    Session CSRF token generation and validation support.
    """

    csrf = True
    csrf_class = SessionCSRF

    @property
    def csrf_secret(self):
        secret_key = current_app.secret_key
        return derive_key(secret_key, "csrf")

    @property
    def csrf_context(self):
        return session

    @property
    def csrf_time_limit(self):
        return timedelta(minutes=30)
