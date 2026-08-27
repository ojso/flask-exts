import pytest
from flask import g
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_exts.forms.form import Form
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
