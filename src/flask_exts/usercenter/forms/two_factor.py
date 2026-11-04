from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

from . import Form


class TwoFactorForm(Form):
    code = StringField("2FA Code", validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField("Verify")
