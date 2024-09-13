from flask import request
from flask import session
from flask import current_app

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




