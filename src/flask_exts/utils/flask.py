from flask import g
from flask import flash
from flask_babel import gettext


def get_template_args():
    args = getattr(g, "_admin_template_args", None)
    if args is None:
        args = g._admin_template_args = dict()
    return args


def flash_errors(form, message):
    for field_name, errors in form.errors.items():
        errors = form[field_name].label.text + ": " + ", ".join(errors)
        flash(gettext(message, error=str(errors)), "error")
