from wtforms.fields import Field

from ..validators.recaptcha import Recaptcha
from ..widgets.recaptcha import RecaptchaWidget


class RecaptchaField(Field):
    widget = RecaptchaWidget()

    # error message if recaptcha validation fails
    recaptcha_error = None

    def __init__(self, label="", validators=None, **kwargs):
        validators = validators or [Recaptcha()]
        super().__init__(label, validators, **kwargs)
