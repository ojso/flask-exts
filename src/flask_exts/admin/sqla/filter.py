import enum
from flask_babel import lazy_gettext
from sqlalchemy.sql import not_, or_
from ..model import filter
from ..model.filter import BaseFilter
from ..model.filter import BaseBooleanFilter
from ..model.filter import BaseIntFilter
from ..model.filter import BaseFloatFilter
from ..model.filter import BaseDateFilter
from ..model.filter import BaseDateTimeFilter
from ..model.filter import BaseTimeFilter
from ...datastore.sqla.utils import parse_like_term
from .query import Query


class BaseSQLAFilter(BaseFilter):
    """
    Base SQLAlchemy filter.
    """

    def __init__(self, column: str, name, options=None, data_type=None):
        """
        Constructor.

        :param column:
            Model field
        :param name:
            Display name
        :param options:
            Fixed set of options
        :param data_type:
            Client data type
        """
        super().__init__(name, options, data_type)

        self.column = column


class FilterEqual(BaseSQLAFilter):
    def apply(self, query: Query, value):
        return query.add_filter(self.column, value, "==")

    def operation(self):
        return lazy_gettext("equals")


class FilterNotEqual(BaseSQLAFilter):
    def apply(self, query, value, alias=None):
        return query.filter(self.get_column(alias) != value)

    def operation(self):
        return lazy_gettext("not equal")


class FilterLike(BaseSQLAFilter):
    def apply(self, query, value, alias=None):
        stmt = parse_like_term(value)
        return query.filter(self.get_column(alias).ilike(stmt))

    def operation(self):
        return lazy_gettext("contains")


class FilterNotLike(BaseSQLAFilter):
    def apply(self, query, value, alias=None):
        stmt = parse_like_term(value)
        return query.filter(~self.get_column(alias).ilike(stmt))

    def operation(self):
        return lazy_gettext("not contains")


class FilterGreater(BaseSQLAFilter):
    def apply(self, query, value, alias=None):
        return query.filter(self.get_column(alias) > value)

    def operation(self):
        return lazy_gettext("greater than")


class FilterSmaller(BaseSQLAFilter):
    def apply(self, query, value, alias=None):
        return query.filter(self.get_column(alias) < value)

    def operation(self):
        return lazy_gettext("smaller than")


class FilterEmpty(BaseSQLAFilter, BaseBooleanFilter):
    def apply(self, query, value, alias=None):
        if value == "1":
            return query.filter(self.get_column(alias).is_(None))
        else:
            return query.filter(self.get_column(alias).is_not(None))

    def operation(self):
        return lazy_gettext("empty")


class FilterInList(BaseSQLAFilter):
    def __init__(self, column, name, options=None, data_type=None):
        super().__init__(column, name, options, data_type="select2-tags")

    def clean(self, value):
        return [v.strip() for v in value.split(",") if v.strip()]

    def apply(self, query, value, alias=None):
        return query.filter(self.get_column(alias).in_(value))

    def operation(self):
        return lazy_gettext("in list")


class FilterNotInList(FilterInList):
    def apply(self, query, value, alias=None):
        # NOT IN can exclude NULL values, so "or_ == None" needed to be added
        column = self.get_column(alias)
        return query.filter(or_(~column.in_(value), column.is_(None)))

    def operation(self):
        return lazy_gettext("not in list")


# Customized type filters
class BooleanEqualFilter(FilterEqual, BaseBooleanFilter):
    pass


class BooleanNotEqualFilter(FilterNotEqual, BaseBooleanFilter):
    pass


class IntEqualFilter(FilterEqual, BaseIntFilter):
    pass


class IntNotEqualFilter(FilterNotEqual, BaseIntFilter):
    pass


class IntGreaterFilter(FilterGreater, BaseIntFilter):
    pass


class IntSmallerFilter(FilterSmaller, BaseIntFilter):
    pass


class IntInListFilter(filter.BaseIntListFilter, FilterInList):
    pass


class IntNotInListFilter(filter.BaseIntListFilter, FilterNotInList):
    pass


class FloatEqualFilter(FilterEqual, filter.BaseFloatFilter):
    pass


class FloatNotEqualFilter(FilterNotEqual, filter.BaseFloatFilter):
    pass


class FloatGreaterFilter(FilterGreater, filter.BaseFloatFilter):
    pass


class FloatSmallerFilter(FilterSmaller, filter.BaseFloatFilter):
    pass


class FloatInListFilter(filter.BaseFloatListFilter, FilterInList):
    pass


class FloatNotInListFilter(filter.BaseFloatListFilter, FilterNotInList):
    pass


class DateEqualFilter(FilterEqual, filter.BaseDateFilter):
    pass


class DateNotEqualFilter(FilterNotEqual, filter.BaseDateFilter):
    pass


class DateGreaterFilter(FilterGreater, filter.BaseDateFilter):
    pass


class DateSmallerFilter(FilterSmaller, filter.BaseDateFilter):
    pass


class DateBetweenFilter(BaseSQLAFilter, filter.BaseDateBetweenFilter):
    def __init__(self, column, name, options=None, data_type=None):
        super().__init__(column, name, options, data_type="daterangepicker")

    def apply(self, query, value, alias=None):
        start, end = value
        return query.filter(self.get_column(alias).between(start, end))


class DateNotBetweenFilter(DateBetweenFilter):
    def apply(self, query, value, alias=None):
        start, end = value
        return query.filter(not_(self.get_column(alias).between(start, end)))

    def operation(self):
        return lazy_gettext("not between")


class DateTimeEqualFilter(FilterEqual, filter.BaseDateTimeFilter):
    pass


class DateTimeNotEqualFilter(FilterNotEqual, filter.BaseDateTimeFilter):
    pass


class DateTimeGreaterFilter(FilterGreater, filter.BaseDateTimeFilter):
    pass


class DateTimeSmallerFilter(FilterSmaller, filter.BaseDateTimeFilter):
    pass


class DateTimeBetweenFilter(BaseSQLAFilter, filter.BaseDateTimeBetweenFilter):
    def __init__(self, column, name, options=None, data_type=None):
        super().__init__(column, name, options, data_type="datetimerangepicker")

    def apply(self, query, value, alias=None):
        start, end = value
        return query.filter(self.get_column(alias).between(start, end))


class DateTimeNotBetweenFilter(DateTimeBetweenFilter):
    def apply(self, query, value, alias=None):
        start, end = value
        return query.filter(not_(self.get_column(alias).between(start, end)))

    def operation(self):
        return lazy_gettext("not between")


class TimeEqualFilter(FilterEqual, filter.BaseTimeFilter):
    pass


class TimeNotEqualFilter(FilterNotEqual, filter.BaseTimeFilter):
    pass


class TimeGreaterFilter(FilterGreater, filter.BaseTimeFilter):
    pass


class TimeSmallerFilter(FilterSmaller, filter.BaseTimeFilter):
    pass


class TimeBetweenFilter(BaseSQLAFilter, filter.BaseTimeBetweenFilter):
    def __init__(self, column, name, options=None, data_type=None):
        super().__init__(column, name, options, data_type="timerangepicker")

    def apply(self, query, value, alias=None):
        start, end = value
        return query.filter(self.get_column(alias).between(start, end))


class TimeNotBetweenFilter(TimeBetweenFilter):
    def apply(self, query, value, alias=None):
        start, end = value
        return query.filter(not_(self.get_column(alias).between(start, end)))

    def operation(self):
        return lazy_gettext("not between")


class EnumEqualFilter(FilterEqual):
    def __init__(self, column, name, options=None, **kwargs):
        self.enum_class = column.type.enum_class
        super().__init__(column, name, options, **kwargs)

    def clean(self, value):
        if self.enum_class is None:
            return super().clean(value)
        return self.enum_class[value]


class EnumFilterNotEqual(FilterNotEqual):
    def __init__(self, column, name, options=None, **kwargs):
        self.enum_class = column.type.enum_class
        super().__init__(column, name, options, **kwargs)

    def clean(self, value):
        if self.enum_class is None:
            return super().clean(value)
        return self.enum_class[value]


class EnumFilterEmpty(FilterEmpty):
    def __init__(self, column, name, options=None, **kwargs):
        self.enum_class = column.type.enum_class
        super().__init__(column, name, options, **kwargs)


class EnumFilterInList(FilterInList):
    def __init__(self, column, name, options=None, **kwargs):
        self.enum_class = column.type.enum_class
        super().__init__(column, name, options, **kwargs)

    def clean(self, value):
        values = super().clean(value)
        if self.enum_class is not None:
            values = [self.enum_class[val] for val in values]
        return values


class EnumFilterNotInList(FilterNotInList):
    def __init__(self, column, name, options=None, **kwargs):
        self.enum_class = column.type.enum_class
        super().__init__(column, name, options, **kwargs)

    def clean(self, value):
        values = super().clean(value)
        if self.enum_class is not None:
            values = [self.enum_class[val] for val in values]
        return values


class ChoiceTypeEqualFilter(FilterEqual):
    def __init__(self, column, name, options=None, **kwargs):
        super().__init__(column, name, options, **kwargs)

    def apply(self, query, user_query, alias=None):
        column = self.get_column(alias)
        choice_type = None
        # loop through choice 'values' to try and find an exact match
        if isinstance(column.type.choices, enum.EnumMeta):
            for choice in column.type.choices:
                if choice.name == user_query:
                    choice_type = choice.value
                    break
        else:
            for type, value in column.type.choices:
                if value == user_query:
                    choice_type = type
                    break
        if choice_type:
            return query.filter(column == choice_type)
        else:
            return query.filter(column.in_([]))


class ChoiceTypeNotEqualFilter(FilterNotEqual):
    def __init__(self, column, name, options=None, **kwargs):
        super().__init__(column, name, options, **kwargs)

    def apply(self, query, user_query, alias=None):
        column = self.get_column(alias)
        choice_type = None
        # loop through choice 'values' to try and find an exact match
        if isinstance(column.type.choices, enum.EnumMeta):
            for choice in column.type.choices:
                if choice.name == user_query:
                    choice_type = choice.value
                    break
        else:
            for type, value in column.type.choices:
                if value == user_query:
                    choice_type = type
                    break
        if choice_type:
            # != can exclude NULL values, so "or_ == None" needed to be added
            return query.filter(
                or_(column != choice_type, column == None)
            )  # noqa: E711
        else:
            return query


class ChoiceTypeLikeFilter(FilterLike):
    def __init__(self, column, name, options=None, **kwargs):
        super().__init__(column, name, options, **kwargs)

    def apply(self, query, user_query, alias=None):
        column = self.get_column(alias)
        choice_types = []
        if user_query:
            # loop through choice 'values' looking for matches
            if isinstance(column.type.choices, enum.EnumMeta):
                for choice in column.type.choices:
                    if user_query.lower() in choice.name.lower():
                        choice_types.append(choice.value)
            else:
                for type, value in column.type.choices:
                    if user_query.lower() in value.lower():
                        choice_types.append(type)
        if choice_types:
            return query.filter(column.in_(choice_types))
        else:
            return query


class ChoiceTypeNotLikeFilter(FilterNotLike):
    def __init__(self, column, name, options=None, **kwargs):
        super().__init__(column, name, options, **kwargs)

    def apply(self, query, user_query, alias=None):
        column = self.get_column(alias)
        choice_types = []
        if user_query:
            # loop through choice 'values' looking for matches
            if isinstance(column.type.choices, enum.EnumMeta):
                for choice in column.type.choices:
                    if user_query.lower() in choice.name.lower():
                        choice_types.append(choice.value)
            else:
                for type, value in column.type.choices:
                    if user_query.lower() in value.lower():
                        choice_types.append(type)
        if choice_types:
            # != can exclude NULL values, so "or_ == None" needed to be added
            return query.filter(
                or_(column.notin_(choice_types), column == None)
            )  # noqa: E711
        else:
            return query


class FilterConverter:
    string_filters = (
        FilterLike,
        FilterNotLike,
        FilterEqual,
        FilterNotEqual,
        FilterEmpty,
        FilterInList,
        FilterNotInList,
    )
    string_key_filters = (
        FilterEqual,
        FilterNotEqual,
        FilterEmpty,
        FilterInList,
        FilterNotInList,
    )
    int_filters = (
        IntEqualFilter,
        IntNotEqualFilter,
        IntGreaterFilter,
        IntSmallerFilter,
        FilterEmpty,
        IntInListFilter,
        IntNotInListFilter,
    )
    float_filters = (
        FloatEqualFilter,
        FloatNotEqualFilter,
        FloatGreaterFilter,
        FloatSmallerFilter,
        FilterEmpty,
        FloatInListFilter,
        FloatNotInListFilter,
    )
    bool_filters = (BooleanEqualFilter, BooleanNotEqualFilter)
    enum_filters = (
        EnumEqualFilter,
        EnumFilterNotEqual,
        EnumFilterEmpty,
        EnumFilterInList,
        EnumFilterNotInList,
    )
    date_filters = (
        DateEqualFilter,
        DateNotEqualFilter,
        DateGreaterFilter,
        DateSmallerFilter,
        DateBetweenFilter,
        DateNotBetweenFilter,
        FilterEmpty,
    )
    datetime_filters = (
        DateTimeEqualFilter,
        DateTimeNotEqualFilter,
        DateTimeGreaterFilter,
        DateTimeSmallerFilter,
        DateTimeBetweenFilter,
        DateTimeNotBetweenFilter,
        FilterEmpty,
    )
    time_filters = (
        TimeEqualFilter,
        TimeNotEqualFilter,
        TimeGreaterFilter,
        TimeSmallerFilter,
        TimeBetweenFilter,
        TimeNotBetweenFilter,
        FilterEmpty,
    )
    choice_type_filters = (
        ChoiceTypeEqualFilter,
        ChoiceTypeNotEqualFilter,
        ChoiceTypeLikeFilter,
        ChoiceTypeNotLikeFilter,
        FilterEmpty,
    )

    arrow_type_filters = (DateTimeGreaterFilter, DateTimeSmallerFilter, FilterEmpty)

    TYPE_MAPPING = {
        "string_filters": [
            "string",
            "char",
            "unicode",
            "varchar",
            "tinytext",
            "text",
            "mediumtext",
            "longtext",
            "unicodetext",
            "nchar",
            "nvarchar",
            "ntext",
            "citext",
            "emailtype",
            "URLType",
            "IPAddressType",
        ],
        "string_key_filters": ["ColorType", "TimezoneType", "CurrencyType"],
        "bool_filters": ["boolean", "tinyint"],
        "int_filters": [
            "int",
            "integer",
            "smallinteger",
            "smallint",
            "biginteger",
            "bigint",
            "mediumint",
        ],
        "float_filters": [
            "float",
            "real",
            "decimal",
            "numeric",
            "double_precision",
            "double",
        ],
        "date_filters": ["date"],
        "datetime_filters": ["datetime", "datetime2", "timestamp", "smalldatetime"],
        "time_filters": ["time"],
        "choice_type_filters": ["ChoiceType"],
        "enum_filters": ["enum"],
    }

    def __init__(self):
        self._converters = {}
        for filter_attr_name, db_types in self.TYPE_MAPPING.items():
            filters = getattr(self, filter_attr_name, None)
            if filters:
                for t in db_types:
                    self._converters[t.lower()] = filters

    def get_filters(self, column_type, column, name, **kwargs):
        column_type_name = column_type.lower()
        filters = self._converters.get(column_type_name, None)
        if column_type_name == "enum":
            options = [(v, v) for v in column.type.enums]
            kwargs["options"] = options
        if filters:
            return [f(column, name, **kwargs) for f in filters]
