import pytest
from flask import g, session
from itsdangerous import BadSignature, URLSafeTimedSerializer
from wtforms import StringField
from wtforms.validators import DataRequired

from flask_exts.forms.form import Form
from flask_exts.forms.form.csrf import CSRF_SALT, get_csrf_token
from flask_exts.security.keys import derive_key
from tests.forms.common import DummyPostData


class F(Form):
    a = StringField(validators=[DataRequired()])


def test_from(app):
    with pytest.raises(RuntimeError):
        f = F()
    with app.app_context():
        f = F()


def test_csrf_form(app):
    app.config.update(CSRF_ENABLED=True)
    with app.test_request_context():
        assert g.get("csrf_token") is None
        f = F()
        assert g.get("csrf_token") is not None
        assert "a" in f
        assert "csrf_token" in f
        f = F(a="foo")
        assert f.a.data == "foo"
        assert f.validate() is False
        f = F(a="foo", csrf_token=g.get("csrf_token"))
        assert f.validate()
        # formdata
        formdata = DummyPostData(a="bar", csrf_token=g.get("csrf_token"))
        assert f.validate()


def test_csrf_token_uses_derived_key(app):
    with app.test_request_context():
        csrf_token = get_csrf_token()
        expected_serializer = URLSafeTimedSerializer(
            derive_key(app.secret_key, "csrf"), salt=CSRF_SALT
        )
        legacy_serializer = URLSafeTimedSerializer(app.secret_key, salt=CSRF_SALT)

        assert expected_serializer.loads(csrf_token) == session["csrf_token"]
        with pytest.raises(BadSignature):
            legacy_serializer.loads(csrf_token)


def test_nocsrf_form(app):
    app.config.update(CSRF_ENABLED=False)
    with app.test_request_context():
        f = F()
        assert "a" in f
        assert "csrf_token" not in f
        assert g.get("csrf_token") is None
        f = F(a="foo")
        assert f.a.data == "foo"
        assert f.validate()
