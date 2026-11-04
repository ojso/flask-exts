from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length

from . import Form


class ResetPasswordForm(Form):
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=50)]
    )
    password_repeat = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Reset Password")
