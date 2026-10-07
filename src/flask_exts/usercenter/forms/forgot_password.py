from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from . import Form


class ForgotPasswordForm(Form):
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Send Reset Password Email")

    def validate(self, **kwargs):
        return super().validate(**kwargs)
