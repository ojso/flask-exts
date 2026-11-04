from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

from . import Form


class RecoveryForm(Form):
    code = StringField(
        "Recovery Code", validators=[DataRequired(), Length(min=6, max=32)]
    )
    submit = SubmitField("Recover")
