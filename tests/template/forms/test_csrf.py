import pytest
from flask import g
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_exts.template.form.flask_form import FlaskForm


class F(FlaskForm):
    name = StringField(validators=[DataRequired()])


def test_csrf_form(app):
    with app.test_request_context():
        assert g.get("csrf_token") is None
        form = F()
        assert g.get("csrf_token") is not None
        assert "name" in form
        assert "csrf_token" in form
        data = {"name": "test"}
        form.process(data=data)
        assert form.name.data == "test"
        assert form.validate() is False
        data2 = {"name": "test", "csrf_token": g.get("csrf_token")}
        form.process(data=data2)
        assert form.validate()


def test_nocsrf_form(app):
    app.config.update(CSRF_ENABLED=False)
    with app.test_request_context():
        form = F()
        assert "name" in form
        assert "csrf_token" not in form
        assert g.get("csrf_token") is None
        data = {"name": "test"}
        form.process(data=data)
        assert form.name.data == "test"
        assert form.validate()
