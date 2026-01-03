from sqlalchemy.sql import not_, or_
import enum
from flask_babel import lazy_gettext
from . import utils
from ..model import filter
from ...datastore.sqla.utils import parse_like_term

class BaseSQLAFilter(filter.BaseFilter):
    """
    Base SQLAlchemy filter.
    """

    def __init__(self, column, name, options=None, data_type=None):
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

    def get_column(self, alias):
        return self.column if alias is None else getattr(alias, self.column.key)

    def apply(self, query, value, alias=None):
        return super().apply(query, value)


# Common filters
class FilterEqual(BaseSQLAFilter):
    def apply(self, query, value, alias=None):
        return query.filter(self.get_column(alias) == value)

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


class FilterEmpty(BaseSQLAFilter, filter.BaseBooleanFilter):
    def apply(self, query, value, alias=None):
        if value == "1":
            return query.filter(self.get_column(alias) == None)  # noqa: E711
        else:
            return query.filter(self.get_column(alias) != None)  # noqa: E711

    def operation(self):
        return lazy_gettext("empty")


class FilterInList(BaseSQLAFilter):
    def __init__(self, column, name, options=None, data_type=None):
        super().__init__(
            column, name, options, data_type="select2-tags"
        )

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
        return query.filter(or_(~column.in_(value), column == None))  # noqa: E711

    def operation(self):
        return lazy_gettext("not in list")


# Customized type filters
class BooleanEqualFilter(FilterEqual, filter.BaseBooleanFilter):
    pass


class BooleanNotEqualFilter(FilterNotEqual, filter.BaseBooleanFilter):
    pass


class IntEqualFilter(FilterEqual, filter.BaseIntFilter):
    pass


class IntNotEqualFilter(FilterNotEqual, filter.BaseIntFilter):
    pass


class IntGreaterFilter(FilterGreater, filter.BaseIntFilter):
    pass


class IntSmallerFilter(FilterSmaller, filter.BaseIntFilter):
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
        super().__init__(
            column, name, options, data_type="daterangepicker"
        )

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
        super().__init__(
            column, name, options, data_type="datetimerangepicker"
        )

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
        super().__init__(
            column, name, options, data_type="timerangepicker"
        )

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


class UuidFilterEqual(FilterEqual, filter.BaseUuidFilter):
    pass


class UuidFilterNotEqual(FilterNotEqual, filter.BaseUuidFilter):
    pass


class UuidFilterInList(filter.BaseUuidListFilter, FilterInList):
    pass


class UuidFilterNotInList(filter.BaseUuidListFilter, FilterNotInList):
    pass


# Base SQLA filter field converter
class FilterConverter(filter.BaseFilterConverter):
    strings = (
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
    enum = (
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
    uuid_filters = (
        UuidFilterEqual,
        UuidFilterNotEqual,
        FilterEmpty,
        UuidFilterInList,
        UuidFilterNotInList,
    )
    arrow_type_filters = (DateTimeGreaterFilter, DateTimeSmallerFilter, FilterEmpty)

    def convert(self, type_name, column, name, **kwargs):
        filter_name = type_name.lower()

        if filter_name in self.converters:
            return self.converters[filter_name](column, name, **kwargs)

        return None

    @filter.convert(
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
    )
    def conv_string(self, column, name, **kwargs):
        return [f(column, name, **kwargs) for f in self.strings]

    @filter.convert("UUIDType", "ColorType", "TimezoneType", "CurrencyType")
    def conv_string_keys(self, column, name, **kwargs):
        return [f(column, name, **kwargs) for f in self.string_key_filters]

    @filter.convert("boolean", "tinyint")
    def conv_bool(self, column, name, **kwargs):
        return [f(column, name, **kwargs) for f in self.bool_filters]

    @filter.convert(
        "int",
        "integer",
        "smallinteger",
        "smallint",
        "biginteger",
        "bigint",
        "mediumint",
    )
    def conv_int(self, column, name, **kwargs):
        return [f(column, name, **kwargs) for f in self.int_filters]

    @filter.convert(
        "float", "real", "decimal", "numeric", "double_precision", "double"
    )
    def conv_float(self, column, name, **kwargs):
        return [f(column, name, **kwargs) for f in self.float_filters]

    @filter.convert("date")
    def conv_date(self, column, name, **kwargs):
        return [f(column, name, **kwargs) for f in self.date_filters]

    @filter.convert("datetime", "datetime2", "timestamp", "smalldatetime")
    def conv_datetime(self, column, name, **kwargs):
        return [f(column, name, **kwargs) for f in self.datetime_filters]

    @filter.convert("time")
    def conv_time(self, column, name, **kwargs):
        return [f(column, name, **kwargs) for f in self.time_filters]

    @filter.convert("ChoiceType")
    def conv_sqla_utils_choice(self, column, name, **kwargs):
        return [f(column, name, **kwargs) for f in self.choice_type_filters]

    @filter.convert("enum")
    def conv_enum(self, column, name, options=None, **kwargs):
        if not options:
            options = [(v, v) for v in column.type.enums]

        return [f(column, name, options, **kwargs) for f in self.enum]

    @filter.convert("uuid")
    def conv_uuid(self, column, name, **kwargs):
        return [f(column, name, **kwargs) for f in self.uuid_filters]
