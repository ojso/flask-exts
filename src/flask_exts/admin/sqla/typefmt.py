from sqlalchemy.ext.associationproxy import _AssociationList
from sqlalchemy.orm.collections import InstrumentedList
from ..model.typefmt import BASE_FORMATTERS, EXPORT_FORMATTERS, list_formatter


def choice_formatter(view, choice, name) -> str:
    """
    Return label of selected choice
    see https://sqlalchemy-utils.readthedocs.io/

    :param choice:
        sqlalchemy_utils Choice, which has a `code` and a `value`
    """
    return choice.value



DEFAULT_FORMATTERS = BASE_FORMATTERS.copy()
EXPORT_FORMATTERS = EXPORT_FORMATTERS.copy()

DEFAULT_FORMATTERS.update(
    {
        InstrumentedList: list_formatter,
        _AssociationList: list_formatter,
    }
)



