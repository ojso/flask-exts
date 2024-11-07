from wtforms import StringField
from wtforms import PasswordField
from wtforms import BooleanField
from wtforms import SubmitField
from wtforms.validators import ValidationError
from wtforms.validators import DataRequired
from wtforms.validators import EqualTo
from wtforms.validators import Length

from ..form import FlaskForm

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("login")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=6, max=50)]
    )
    # email = StringField('Email', validators=[DataRequired(), Email()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=50)]
    )
    password_repeat = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        return

    def validate_email(self, email):
        return


class ProfileForm(FlaskForm):
    email = StringField("Email")
    submit = SubmitField("Submit")

    def validate_email(self, email):
        return
