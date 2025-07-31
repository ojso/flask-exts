import hashlib
import hmac
import os
from flask import g
from flask import session
from flask import current_app
from itsdangerous import BadData
from itsdangerous import SignatureExpired
from itsdangerous import URLSafeTimedSerializer
from wtforms import ValidationError
from wtforms.csrf.core import CSRF

CSRF_FIELD_NAME = "csrf_token"
CSRF_SALT = "csrf-salt"
CSRF_TIME_LIMIT = 1800


def _get_csrf_token_of_session_and_g():
    """Generate CSRF token of session and g for the current request."""
    csrf_secret_key = current_app.config.get("CSRF_SECRET_KEY", current_app.secret_key)
    csrf_field_name = current_app.config.get("CSRF_FIELD_NAME", CSRF_FIELD_NAME)

    if csrf_field_name not in g:
        s = URLSafeTimedSerializer(csrf_secret_key, salt=CSRF_SALT)
        if csrf_field_name not in session:
            session[csrf_field_name] = hashlib.sha1(os.urandom(64)).hexdigest()
        token = s.dumps(session[csrf_field_name])
        setattr(g, csrf_field_name, token)
    return session.get(csrf_field_name), g.get(csrf_field_name)


def get_or_generate_csrf_token():
    _, g_csrf_token = _get_csrf_token_of_session_and_g()
    return g_csrf_token


class FlaskFormCSRF(CSRF):
    def setup_form(self, form):
        self.meta = form.meta
        return super().setup_form(form)

    def generate_csrf_token(self, csrf_token_field):
        return get_or_generate_csrf_token()

    def validate_csrf_token(self, form, field):
        csrf_secret_key = current_app.config.get(
            "CSRF_SECRET_KEY", current_app.secret_key
        )
        csrf_field_name = current_app.config.get("CSRF_FIELD_NAME", CSRF_FIELD_NAME)
        csrf_time_limit = current_app.config.get("CSRF_TIME_LIMIT", CSRF_TIME_LIMIT)

        data = field.data
        if not data:
            raise ValidationError("The CSRF token is missing.")
        if csrf_field_name not in session:
            raise ValidationError("The CSRF session token is missing.")
        s = URLSafeTimedSerializer(csrf_secret_key, salt=CSRF_SALT)
        try:
            token = s.loads(data, max_age=csrf_time_limit)
        except SignatureExpired as e:
            raise ValidationError(field.gettext("CSRF token expired.")) from e
        except BadData as e:
            raise ValidationError("The CSRF token is invalid.") from e
        if not hmac.compare_digest(session[csrf_field_name], token):
            raise ValidationError("The CSRF tokens do not match.")
