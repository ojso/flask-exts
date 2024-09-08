from flask_babel import Babel
from flask_babel import get_locale
from .admin_domain import _gettext, _ngettext, _lazy_gettext
from .settings import locale_selector, timezone_selector

babel = Babel()


def babel_init_app(app):
    babel.init_app(
        app, locale_selector=locale_selector, timezone_selector=timezone_selector
    )

    @app.context_processor
    def get_lang():
        return {"lang": get_locale()}

    @app.context_processor
    def get_admin_translation():
        return {"_gettext": _gettext, "_ngettext": _ngettext}
