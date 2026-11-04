from flask_login import current_user
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length

from . import Form


class ChangePasswordForm(Form):
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
