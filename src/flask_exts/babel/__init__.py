from flask_babel import Babel
from flask_babel import get_locale
from .selector import locale_selector, timezone_selector

from .. import translations
from wtforms.i18n import messages_path

babel = Babel()


def babel_init_app(app):
    wtforms_domain = {"translation_directory": messages_path(), "domain": "wtforms"}

    exts_domain = {
        "translation_directory": translations.__path__[0],
        "domain": "messages",
    }

    app_directory = app.config.get(
        "BABEL_TRANSLATION_DIRECTORIES", "translations"
    ).split(";")
    app_domain = app.config.get("BABEL_DOMAIN", "messages").split(";")

    translation_directories = [
        wtforms_domain["translation_directory"],
        exts_domain["translation_directory"],
    ] + app_directory

    domains = [
        wtforms_domain["domain"],
        exts_domain["domain"],
    ] + app_domain

    babel.init_app(
        app,
        default_translation_directories=";".join(translation_directories),
        default_domain=";".join(domains),
        locale_selector=locale_selector,
        timezone_selector=timezone_selector,
    )

    @app.context_processor
    def get_lang():
        return {"lang": get_locale()}
