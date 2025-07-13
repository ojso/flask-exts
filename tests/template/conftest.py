import pytest
from wtforms import BooleanField, PasswordField, StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length
from flask_exts.template.form.flask_form import FlaskForm


class HelloForm(FlaskForm):
    name = StringField("Name")
    username = StringField("Username", validators=[DataRequired(), Length(1, 20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(8, 150)])
    remember = BooleanField("Remember me")
    hidden = HiddenField()
    submit = SubmitField()


@pytest.fixture
def hello_form():
    return HelloForm
