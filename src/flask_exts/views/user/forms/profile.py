from wtforms import StringField
from wtforms import SubmitField
from . import Form


class ProfileForm(Form):
    email = StringField("Email")
    submit = SubmitField("Submit")

    def validate_email(self, email):
        return
