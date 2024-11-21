from ...forms.form import FlaskForm
from python_plugins.forms.mixins.user import RegisterForm as MixRegisterForm


class RegisterForm(FlaskForm, MixRegisterForm):
    pass
