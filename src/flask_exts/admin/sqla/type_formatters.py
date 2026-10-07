from sqlalchemy.ext.associationproxy import _AssociationList
from sqlalchemy.orm.collections import InstrumentedList

from ..model.type_formatters import BASE_FORMATTERS, list_formatter

DEFAULT_FORMATTERS = BASE_FORMATTERS.copy()
DEFAULT_FORMATTERS.update(
    {
        InstrumentedList: list_formatter,
        _AssociationList: list_formatter,
    }
)
