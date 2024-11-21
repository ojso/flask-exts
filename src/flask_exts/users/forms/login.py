from python_plugins.forms.mixins.user import LoginForm as MixLoginForm
from ...forms.form import FlaskForm


class LoginForm(FlaskForm, MixLoginForm):
    pass
