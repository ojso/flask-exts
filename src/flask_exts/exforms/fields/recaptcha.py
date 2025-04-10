from wtforms.fields import Field
from ..widgets.recaptcha import RecaptchaWidget
from ..validators.recaptcha import Recaptcha


class RecaptchaField(Field):
    widget = RecaptchaWidget()

    # error message if recaptcha validation fails
    recaptcha_error = None

    def __init__(self, label="", validators=None, **kwargs):
        validators = validators or [Recaptcha()]
        super().__init__(label, validators, **kwargs)
