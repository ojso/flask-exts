import json
from collections.abc import Callable
from enum import Enum
from typing import Any

from markupsafe import Markup

T_FORMATTERS = dict[type, Callable[[Any, Any, Any], Any]]


def null_formatter(view, value, name):
    """Return `NULL` as the string for `None` value

    Args:
        value:
            Value to check
    """
    return Markup("<i>NULL</i>")


def empty_formatter(view, value, name):
    """Return empty string for `None` value

    Args:
        value:
            Value to check
    """
    return ""


def bool_formatter(view, value, name):
    """Return check icon if value is `True` or empty string otherwise.

    Args:
        value:
            Value to check
    """
    label = f"{name}: {'true' if value else 'false'}"
    return Markup(f'<span title="{label}">{"✓" if value else "✗"}</span>')


def list_formatter(view, values, name) -> str:
    """Return string with comma separated values

    Args:
        values:
            Value to check
    """
    return ", ".join(str(v) for v in values)


def enum_formatter(view, value, name) -> str:
    """Return the name of the enumerated member.

    Args:
        value:
            Value to check
    """
    return value.name


def dict_formatter(view, value, name) -> str:
    """Removes unicode entities when displaying dict as string. Also unescapes

    non-ASCII characters stored in the JSON.

    Args:
        value:
            Dict to convert to string
    """
    return json.dumps(value, ensure_ascii=False)


BASE_FORMATTERS: T_FORMATTERS = {
    type(None): empty_formatter,
    bool: bool_formatter,
    list: list_formatter,
    dict: dict_formatter,
    Enum: enum_formatter,
}

EXPORT_FORMATTERS: T_FORMATTERS = {
    type(None): empty_formatter,
    list: list_formatter,
    dict: dict_formatter,
    Enum: enum_formatter,
}

DETAIL_FORMATTERS: T_FORMATTERS = {
    type(None): empty_formatter,
    list: list_formatter,
    dict: dict_formatter,
    Enum: enum_formatter,
}
