from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from ..form.flask_form import FlaskForm
from ...proxies import _userstore


class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Send Reset Password Email")

    def validate(self, **kwargs):
        if not super().validate(**kwargs):
            return False
        user = _userstore.get_user_by_identity(self.email.data, "email")
        if user is None or not user.email_verified:
            self.email.errors.append("Found no user with this email")
            return False
        return True
