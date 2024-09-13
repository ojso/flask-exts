from flask import current_app
from flask import session

from werkzeug.utils import cached_property
from wtforms.meta import DefaultMeta

# from wtforms.i18n import get_translations
from flask_babel import get_translations
from flask_babel import get_locale
from .csrf import FlaskFormCSRF
from ...utils import get_formdata


# CSRF_ENABLED = True
CSRF_ENABLED = False
CSRF_FIELD_NAME = "csrf_token"
CSRF_TIME_LIMIT = 1800


class FlaskMeta(DefaultMeta):
    # csrf_class = SessionCSRF  # 安全性较低，也可使用
    csrf_class = FlaskFormCSRF
    csrf_context = session  # not used, provided for custom csrf_class

    @cached_property
    def csrf(self):
        return current_app.config.get("CSRF_ENABLED", CSRF_ENABLED)

    @cached_property
    def csrf_secret(self):
        return current_app.config.get("CSRF_SECRET_KEY", current_app.secret_key)

    @cached_property
    def csrf_field_name(self):
        return current_app.config.get("CSRF_FIELD_NAME", CSRF_FIELD_NAME)

    @cached_property
    def csrf_time_limit(self):
        return current_app.config.get("CSRF_TIME_LIMIT", CSRF_TIME_LIMIT)

    def wrap_formdata(self, form, formdata):
        if formdata is None:
            return get_formdata()
        return formdata

    def get_translations(self, form):
        """get locales from flask_babel.get_locale()

        :param form: _description_
        :return: _description_
        """
        if get_locale() is None:
            return
        return get_translations()
