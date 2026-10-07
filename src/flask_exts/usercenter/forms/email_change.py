from flask_login import current_user
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError

from ...proxies import current_userstore
from . import Form


class EmailChangeForm(Form):
    email = StringField("New Email", validators=[DataRequired(), Email()])
    current_password = PasswordField(
        "Current Password", validators=[DataRequired(), Length(min=3, max=50)]
    )
    submit = SubmitField("Change Email")

    def validate_email(self, email):
        existing_user = current_userstore.get_user_by_identity(email.data, "email")
        if existing_user is not None and (
            not current_user.is_authenticated or existing_user.id != current_user.id
        ):
            raise ValidationError("Email already exists.")

    def validate(self, **kwargs):
        if not super().validate(**kwargs):
            return False
        if not current_user.check_password(self.current_password.data):
            self.current_password.errors.append("Invalid password.")
            return False
        return True
