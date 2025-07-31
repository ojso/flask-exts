from flask import current_app
from flask import session
from werkzeug.utils import cached_property
from wtforms.meta import DefaultMeta

# from wtforms.i18n import get_translations
from flask_babel import get_translations
from flask_babel import get_locale
from .csrf import FlaskFormCSRF
from .csrf import CSRF_FIELD_NAME
from .utils import get_form_data

CSRF_ENABLED = True


class FlaskMeta(DefaultMeta):
    csrf_class = FlaskFormCSRF

    @cached_property
    def csrf(self):
        return current_app.config.get("CSRF_ENABLED", CSRF_ENABLED)

    @cached_property
    def csrf_field_name(self):
        return current_app.config.get("CSRF_FIELD_NAME", CSRF_FIELD_NAME)

    def wrap_formdata(self, form, formdata):
        if formdata is None:
            return get_form_data()
        return formdata

    def get_translations(self, form):
        if get_locale() is None:
            return
        return get_translations()
