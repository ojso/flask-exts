from functools import reduce
from flask import flash
from flask_babel import gettext
from .url import prettify_class_name
from .url import get_redirect_target
from .simple import prettify_name
from .simple import get_mdict_item_or_list


def flash_errors(form, message):
    for field_name, errors in form.errors.items():
        errors = form[field_name].label.text + ": " + ", ".join(errors)
        flash(gettext(message, error=str(errors)), "error")

def rec_getattr(obj, attr):
    """
        Recursive getattr.

        :param attr:
            Dot delimited attribute name
        :param default:
            Default value

        Example::

            rec_getattr(obj, 'a.b.c')
    """
    return reduce(getattr, attr.split('.'), obj)
