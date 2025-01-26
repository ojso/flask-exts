from re import compile
from urllib.parse import urljoin, urlparse
from flask import request
from flask import g
from flask import flash
from flask_babel import gettext

VALID_SCHEMES = ["http", "https"]

_substitute_whitespace = compile(r"[\s\x00-\x08\x0B\x0C\x0E-\x19]+").sub
_fix_multiple_slashes = compile(r"(^([^/]+:)?//)/*").sub

def get_template_args():
    args = getattr(g, "_admin_template_args", None)
    if args is None:
        args = g._admin_template_args = dict()
    return args

def flash_errors(form, message):
    for field_name, errors in form.errors.items():
        errors = form[field_name].label.text + ": " + ", ".join(errors)
        flash(gettext(message, error=str(errors)), "error")


def is_safe_url(target):
    # prevent urls like "\\www.google.com"
    # some browser will change \\ to // (eg: Chrome)
    # refs https://stackoverflow.com/questions/10438008
    target = target.replace("\\", "/")

    # handle cases like "j a v a s c r i p t:"
    target = _substitute_whitespace("", target)

    # Chrome and FireFox "fix" more than two slashes into two after protocol
    target = _fix_multiple_slashes(lambda m: m.group(1), target, 1)

    # prevent urls starting with "javascript:"
    target_info = urlparse(target)
    target_scheme = target_info.scheme
    if target_scheme and target_scheme not in VALID_SCHEMES:
        return False

    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return ref_url.netloc == test_url.netloc


def get_redirect_target(param_name="url"):
    target = request.values.get(param_name)

    if target and is_safe_url(target):
        return target
