from flask import request
from flask import g
from flask import current_app
from flask import session
from itsdangerous import URLSafeTimedSerializer
import hashlib
import os
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.datastructures import ImmutableMultiDict
from wtforms.fields.core import UnboundField


SUBMIT_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
SALT_CSRF_TOKEN = "csrf-token-salt"


def is_form_submitted():
    """Check if current method is PUT or POST"""
    return request and request.method in SUBMIT_METHODS


def get_form_data():
    """If current method is PUT or POST,
    return concatenated `request.form` with `request.files` or `None` otherwise.
    """
    if is_form_submitted():
        if request.files:
            return CombinedMultiDict((request.files, request.form))
        elif request.form:
            return request.form
        elif request.is_json:
            return ImmutableMultiDict(request.get_json())
    return None


def validate_form_on_submit(form):
    """
    If current method is PUT or POST, validate form and return validation status.
    """
    return is_form_submitted() and form.validate()


def recreate_field(unbound):
    """
    Create new instance of the unbound field, resetting wtforms creation counter.

    :param unbound:
        UnboundField instance
    """
    if not isinstance(unbound, UnboundField):
        raise ValueError(
            "recreate_field expects UnboundField instance, %s was passed."
            % type(unbound)
        )

    return unbound.field_class(*unbound.args, **unbound.kwargs)


def generate_csrf():
    """Generate CSRF token for the current request.
    Same to FlaskFormCSRF.generate_csrf_token.
    """
    csrf_field_name = current_app.config.get("CSRF_FIELD_NAME", "csrf_token")
    csrf_secret = current_app.config.get("CSRF_SECRET_KEY", current_app.secret_key)
    if csrf_field_name not in g:
        s = URLSafeTimedSerializer(csrf_secret, salt=SALT_CSRF_TOKEN)
        if csrf_field_name not in session:
            session[csrf_field_name] = hashlib.sha1(os.urandom(64)).hexdigest()
        token = s.dumps(session[csrf_field_name])
        setattr(g, csrf_field_name, token)
    return g.get(csrf_field_name)



