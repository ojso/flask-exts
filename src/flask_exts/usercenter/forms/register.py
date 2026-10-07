from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError

from ...proxies import current_userstore
from . import Form


class RegisterForm(Form):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=6, max=50)]
    )
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=50)]
    )
    password_repeat = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_email(self, email):
        if email.data and current_userstore.get_user_by_identity(email.data, "email"):
            raise ValidationError("Email already exists.")
