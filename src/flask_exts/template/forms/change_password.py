from wtforms import PasswordField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import EqualTo
from wtforms.validators import Length
from flask_login import current_user
from ..form.flask_form import FlaskForm


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        "Old Password", validators=[DataRequired(), Length(min=3, max=50)]
    )
    new_password = PasswordField(
        "New Password", validators=[DataRequired(), Length(min=8, max=50)]
    )
    new_password_repeat = PasswordField(
        "Repeat New Password", validators=[DataRequired(), EqualTo("new_password")]
    )
    submit = SubmitField("Change Password")

    def validate(self, **kwargs):
        if not super().validate(**kwargs):
            return False
        if not current_user.check_password(self.old_password.data):
            self.old_password.errors.append("Invalid password")
            return False
        return True
