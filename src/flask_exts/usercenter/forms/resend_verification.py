from wtforms import SubmitField

from . import Form


class ResendVerificationForm(Form):
    submit = SubmitField("Resend Verification Email")
