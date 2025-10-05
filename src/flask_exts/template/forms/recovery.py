from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from ..form.flask_form import FlaskForm


class RecoveryForm(FlaskForm):
    code = StringField("Recovery Code", validators=[DataRequired(), Length(min=6, max=32)])
    submit = SubmitField("Recover")
