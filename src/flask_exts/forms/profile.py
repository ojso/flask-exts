from wtforms import StringField
from wtforms import SubmitField
from ..exforms import FlaskForm


class ProfileForm(FlaskForm):
    email = StringField("Email")
    submit = SubmitField("Submit")

    def validate_email(self, email):
        return
