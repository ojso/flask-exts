from re import sub, compile
from urllib.parse import urljoin, urlparse
from flask import request
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.datastructures import ImmutableMultiDict
from wtforms import HiddenField


VALID_SCHEMES = ["http", "https"]
SUBMIT_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

_substitute_whitespace = compile(r"[\s\x00-\x08\x0B\x0C\x0E-\x19]+").sub
_fix_multiple_slashes = compile(r"(^([^/]+:)?//)/*").sub


def is_form_submitted():
    """Check if current method is PUT or POST"""
    return request and request.method in SUBMIT_METHODS


def get_form_data():
    """If current method is PUT or POST,
    return concatenated `request.form` with `request.files` or `None` otherwise.
    """
    if is_form_submitted():
        if request.files:
            return CombinedMultiDict((request.files, request.form))
        elif request.form:
            return request.form
        elif request.is_json:
            return ImmutableMultiDict(request.get_json())
    return None


def is_hidden_field_filter(field):
    return isinstance(field, HiddenField)


def get_table_titles(data, primary_key, primary_key_title):
    """Detect and build the table titles tuple from ORM object, currently only support SQLAlchemy."""
    if not data:
        return []
    titles = []
    for k in data[0].__table__.columns.keys():
        if not k.startswith("_"):
            titles.append((k, k.replace("_", " ").title()))
    titles[0] = (primary_key, primary_key_title)
    return titles


def prettify_class_name(name):
    """Split words in PascalCase string into separate words.

    :param name:
        String to split
    """
    return sub(r"(?<=.)([A-Z])", r" \1", name)


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
