import os
from flask_babel import Babel
from flask_babel import get_locale
from .selector import locale_selector, timezone_selector

from .. import translations
from wtforms.i18n import messages_path

babel = Babel()


def babel_init_app(app):
    if "babel" in app.extensions:
        raise RuntimeError("A 'Babel' instance has already been registered.")

    wtforms_domain = {"translation_directory": messages_path(), "domain": "wtforms"}

    exts_domain = {
        "translation_directory": translations.__path__[0],
        "domain": "messages",
    }

    # get app's translation directories and domains from config
    app_directory = app.config.get(
        "BABEL_TRANSLATION_DIRECTORIES", "translations"
    ).split(";")
    app_domain = app.config.get("BABEL_DOMAIN", "messages").split(";")

    app_validate_translation_directories = []
    app_validate_domains = []

    # only add existing directories to the translation directories list and corresponding domains to the domains list
    for path, domain in zip(app_directory, app_domain):
        if not os.path.isabs(path):
            path = os.path.join(app.root_path, path)
        if os.path.exists(path):
            app_validate_translation_directories.append(path)
            app_validate_domains.append(domain)

    translation_directories = [
        wtforms_domain["translation_directory"],
        exts_domain["translation_directory"],
    ] + app_validate_translation_directories

    domains = [
        wtforms_domain["domain"],
        exts_domain["domain"],
    ] + app_validate_domains

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
