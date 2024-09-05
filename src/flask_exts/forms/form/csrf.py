import hashlib
import hmac
import os
from flask import g
from flask import session
from itsdangerous import BadData
from itsdangerous import SignatureExpired
from itsdangerous import URLSafeTimedSerializer
from wtforms import ValidationError
from wtforms.csrf.core import CSRF

SALT_CSRF_TOKEN = "csrf-token-salt"

class FlaskFormCSRF(CSRF):
    def setup_form(self, form):
        self.meta = form.meta
        return super().setup_form(form)

    def generate_csrf_token(self, csrf_token_field):
        meta = self.meta
        secret_key = meta.csrf_secret
        field_name = meta.csrf_field_name

        if field_name not in g:
            s = URLSafeTimedSerializer(secret_key, salt=SALT_CSRF_TOKEN)
            if field_name not in session:
                session[field_name] = hashlib.sha1(os.urandom(64)).hexdigest()
            token = s.dumps(session[field_name])
            setattr(g, field_name, token)

        return g.get(field_name)

    def validate_csrf_token(self, form, field):
        meta = self.meta
        secret_key = meta.csrf_secret
        field_name = meta.csrf_field_name
        time_limit = meta.csrf_time_limit
        data = field.data

        if not data:
            raise ValidationError("The CSRF token is missing.")

        if field_name not in session:
            raise ValidationError("The CSRF session token is missing.")

        s = URLSafeTimedSerializer(secret_key, salt=SALT_CSRF_TOKEN)

        try:
            token = s.loads(data, max_age=time_limit)
        except SignatureExpired as e:
            raise ValidationError(field.gettext("CSRF token expired.")) from e
        except BadData as e:
            raise ValidationError("The CSRF token is invalid.") from e

        if not hmac.compare_digest(session[field_name], token):
            raise ValidationError("The CSRF tokens do not match.")
        


