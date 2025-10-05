from wtforms import PasswordField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import EqualTo
from wtforms.validators import Length
from ..form.flask_form import FlaskForm


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=50)]
    )
    password_repeat = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Reset Password")
