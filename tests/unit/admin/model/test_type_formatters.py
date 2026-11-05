import datetime as dt
import enum

import pytest
from markupsafe import Markup

from flask_exts.admin.model.type_formatters import (
    BASE_FORMATTERS,
    DETAIL_FORMATTERS,
    EXPORT_FORMATTERS,
    null_formatter,
)

FORMATTER_REGISTRIES = [
    pytest.param(BASE_FORMATTERS, id="base"),
    pytest.param(EXPORT_FORMATTERS, id="export"),
    pytest.param(DETAIL_FORMATTERS, id="detail"),
]


class ExampleEnum(enum.Enum):
    first = 1


COMMON_VALUES = [
    pytest.param(None, "", id="none"),
    pytest.param([], "", id="empty-list"),
    pytest.param([1, "two"], "1, two", id="list"),
    pytest.param({}, "{}", id="empty-dict"),
    pytest.param({"name": "中文"}, '{"name": "中文"}', id="dict"),
    pytest.param(ExampleEnum.first, "first", id="enum"),
    pytest.param(dt.time(11, 10, 9), "11:10:09", id="time"),
    pytest.param(
        dt.datetime(2014, 4, 3, 1, 9, 0),
        "2014-04-03 01:09:00",
        id="datetime",
    ),
]

BOOL_VALUES = [
    pytest.param(
        True,
        Markup('<span title="field: true">✓</span>'),
        id="true",
    ),
    pytest.param(
        False,
        Markup('<span title="field: false">✗</span>'),
        id="false",
    ),
]


def _formatter_for(formatters, value):
    for value_type, formatter in formatters.items():
        if isinstance(value, value_type):
            return formatter
    raise AssertionError(f"No formatter registered for {type(value).__name__}")


@pytest.mark.parametrize("formatters", FORMATTER_REGISTRIES)
@pytest.mark.parametrize(("value", "expected"), COMMON_VALUES)
def test_common_formatters(formatters, value, expected):
    formatter = _formatter_for(formatters, value)
    assert formatter(None, value, "field") == expected


@pytest.mark.parametrize(("value", "expected"), BOOL_VALUES)
def test_bool_formatter(value, expected):
    assert BASE_FORMATTERS[bool](None, value, "field") == expected


def test_null_formatter():
    assert null_formatter(None, None, "field") == Markup("<i>NULL</i>")
