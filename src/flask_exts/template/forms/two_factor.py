from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from ..form.flask_form import FlaskForm


class TwoFactorForm(FlaskForm):
    code = StringField("2FA Code", validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField("Verify")
