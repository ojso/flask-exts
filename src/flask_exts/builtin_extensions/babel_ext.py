import os

from flask import (
    current_app,
    request,
    session,
    url_for,
)
from flask_babel import Babel, get_locale
from wtforms.i18n import messages_path

from babel import Locale

from .. import translations
from ..extension_core.base import Extension

babel = Babel()


def locale_selector():
    if not request:
        return
    # save lang to session if lang exists in args
    if request.args.get("lang"):
        session["lang"] = request.args.get("lang")
    # from session
    if session.get("lang"):
        session_lang = session.get("lang")
        return session_lang
    # try to guess the language from the user accept header the browser transmits.
    if current_app.config.get("BABEL_ACCEPT_LANGUAGES"):
        accept_languages = current_app.config["BABEL_ACCEPT_LANGUAGES"].split(";")
        accept_language = request.accept_languages.best_match(accept_languages)
        return accept_language


def _configured_languages():
    """Return the configured locales with names for the language selector."""
    configured = current_app.config.get("BABEL_ACCEPT_LANGUAGES") or ""
    languages = []
    seen = set()
    for code in (item.strip() for item in configured.split(";")):
        if not code or code in seen:
            continue
        seen.add(code)
        try:
            locale = Locale.parse(code.replace("-", "_"))
        except (TypeError, ValueError):
            name = code
        else:
            name = locale.get_display_name(locale)
        languages.append({"code": code, "name": name})
    return languages


def _language_url(code):
    """Return the current URL with the ``lang`` parameter set to ``code``."""
    if request.endpoint is None:
        return f"{request.path}?lang={code}"
    values = dict(request.view_args or ())
    for key, value in request.args.items(multi=True):
        existing = values.get(key)
        if existing is None:
            values[key] = value
        elif isinstance(existing, list):
            existing.append(value)
        else:
            values[key] = [existing, value]
    values["lang"] = code
    return url_for(request.endpoint, **values)


def timezone_selector():
    # save timezone to session if timezone exists in args
    if request.args.get("timezone"):
        session["timezone"] = request.args.get("timezone")
    # from session
    if session.get("timezone"):
        return session.get("timezone")
    # from app.config
    if current_app.config.get("BABEL_DEFAULT_TIMEZONE"):
        return current_app.config.get("BABEL_DEFAULT_TIMEZONE")


class BabelExtension(Extension):
    @property
    def name(self) -> str:
        return "babel"

    def init_app(self, app):
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

        # only add existing directories to the translation directories list and
        # corresponding domains to the domains list
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
            return {
                "lang": get_locale(),
                "babel_languages": _configured_languages(),
                "babel_language_url": _language_url,
            }
