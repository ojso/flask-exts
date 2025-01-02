from ...forms.form import FlaskForm
from .mixins import RegisterForm as MixRegisterForm


class RegisterForm(FlaskForm, MixRegisterForm):
    pass
