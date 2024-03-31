from flask import current_app
from flask import session
from flask import request

from werkzeug.utils import cached_property
from wtforms.meta import DefaultMeta
from wtforms.i18n import get_translations
from flask_babel import get_locale
from .csrf import FlaskFormCSRF
from ..helpers import get_form_data


CSRF_ENABLED = True
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
            return get_form_data()
        return formdata

    def get_translations(self, form):
        """get locales from flask_babel.get_locale()

        :param form: _description_
        :return: _description_
        """
        locales = [get_locale().language]
        # Make locales be a hashable value
        locales = tuple(locales) if locales else None

        if self.cache_translations:
            translations = self.translations_cache.get(locales)
            if translations is None:
                translations = self.translations_cache[locales] = get_translations(
                    locales
                )
            return translations

        return get_translations(locales)
