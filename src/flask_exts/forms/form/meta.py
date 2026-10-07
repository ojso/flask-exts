from flask import current_app, request

# from wtforms.i18n import get_translations
from flask_babel import get_locale, get_translations
from werkzeug.datastructures import CombinedMultiDict, ImmutableMultiDict
from wtforms.meta import DefaultMeta

from .csrf import CSRF_FIELD_NAME, FlaskFormCSRF
from .utils import is_submitted

CSRF_ENABLED = True


class FlaskMeta(DefaultMeta):
    csrf_class = FlaskFormCSRF

    @property
    def csrf(self):
        return current_app.config.get("CSRF_ENABLED", CSRF_ENABLED)

    @property
    def csrf_field_name(self):
        return current_app.config.get("CSRF_FIELD_NAME", CSRF_FIELD_NAME)

    def wrap_formdata(self, form, formdata):
        if formdata is not None:
            return formdata
        elif is_submitted():
            if request.files:
                return CombinedMultiDict((request.files, request.form))
            elif request.form:
                return request.form
            elif request.is_json:
                return ImmutableMultiDict(request.get_json())
        else:
            return None

    def get_translations(self, form):
        if get_locale() is None:
            return
        return get_translations()
