import enum
from flask_babel import lazy_gettext
from sqlalchemy.sql import not_, or_
from ..model.filter import BaseFilterConverter
from ..model.filter import convert_type
from ..model.filter import BaseFilter
from ..model.filter import BaseBooleanFilter
from ..model.filter import BaseIntFilter
from ..model.filter import BaseFloatFilter
from ..model.filter import BaseDateFilter
from ..model.filter import BaseDateTimeFilter
from ..model.filter import BaseTimeFilter
from ..model.filter import BaseIntListFilter
from ..model.filter import BaseFloatListFilter
from ..model.filter import BaseDateBetweenFilter
from ..model.filter import BaseDateTimeBetweenFilter
from ..model.filter import BaseTimeBetweenFilter


class BaseSQLAFilter(BaseFilter):
    """
    Base SQLAlchemy filter.
    """

    def __init__(self, column_type, column: str, name, data_type=None, options=None):
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
        super().__init__(name, data_type, options)
        self.column_type = column_type
        self.column = column


class FilterEqual(BaseSQLAFilter):
    def operation(self):
        return lazy_gettext("equals")

    def apply(self, query, value):
        return query.add_filter(self.column, "==", value)


class FilterNotEqual(BaseSQLAFilter):
    def operation(self):
        return lazy_gettext("not equal")

    def apply(self, query, value):
        return query.add_filter(self.column, "!=", value)


class FilterGreater(BaseSQLAFilter):
    def operation(self):
        return lazy_gettext("greater than")

    def apply(self, query, value):
        return query.add_filter(self.column, ">", value)


class FilterSmaller(BaseSQLAFilter):
    def operation(self):
        return lazy_gettext("smaller than")

    def apply(self, query, value):
        return query.add_filter(self.column, "<", value)


class FilterLike(BaseSQLAFilter):
    def operation(self):
        return lazy_gettext("contains")

    def apply(self, query, value):
        return query.add_filter(self.column, "ilike", value)


class FilterNotLike(BaseSQLAFilter):
    def operation(self):
        return lazy_gettext("not contains")

    def apply(self, query, value):
        return query.add_filter(self.column, "not_ilike", value)


class FilterEmpty(BaseSQLAFilter, BaseBooleanFilter):
    def operation(self):
        return lazy_gettext("empty")

    def apply(self, query, value):
        if value == "1":
            return query.add_filter(self.column, "is_null", None)
        else:
            return query.add_filter(self.column, "isnot_null", None)


class FilterInList(BaseSQLAFilter):
    def __init__(self, column_type, column, name, data_type=None, options=None):
        super().__init__(column_type, column, name, "select2-tags", options)

    def operation(self):
        return lazy_gettext("in list")

    def clean(self, value):
        return [v.strip() for v in value.split(",") if v.strip()]

    def apply(self, query, value):
        return query.add_filter(self.column, "in", value)


class FilterNotInList(FilterInList):
    def operation(self):
        return lazy_gettext("not in list")

    def apply(self, query, value):
        return query.add_filter(self.column, "not_in", value)


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


class IntInListFilter(FilterInList, BaseIntListFilter):
    pass


class IntNotInListFilter(FilterNotInList, BaseIntListFilter):
    pass


class FloatEqualFilter(FilterEqual, BaseFloatFilter):
    pass


class FloatNotEqualFilter(FilterNotEqual, BaseFloatFilter):
    pass


class FloatGreaterFilter(FilterGreater, BaseFloatFilter):
    pass


class FloatSmallerFilter(FilterSmaller, BaseFloatFilter):
    pass


class FloatInListFilter(FilterInList, BaseFloatListFilter):
    pass


class FloatNotInListFilter(FilterNotInList, BaseFloatListFilter):
    pass


class DateEqualFilter(FilterEqual, BaseDateFilter):
    pass


class DateNotEqualFilter(FilterNotEqual, BaseDateFilter):
    pass


class DateGreaterFilter(FilterGreater, BaseDateFilter):
    pass


class DateSmallerFilter(FilterSmaller, BaseDateFilter):
    pass


class DateBetweenFilter(BaseSQLAFilter, BaseDateBetweenFilter):
    def __init__(self, column_type, column, name, data_type=None, options=None):
        super().__init__(column_type, column, name, "daterangepicker", options)

    def apply(self, query, value):
        return query.add_filter(self.column, "between", value)


class DateNotBetweenFilter(DateBetweenFilter):
    def operation(self):
        return lazy_gettext("not between")

    def apply(self, query, value):
        return query.add_filter(self.column, "not_between", value)


class DateTimeEqualFilter(FilterEqual, BaseDateTimeFilter):
    pass


class DateTimeNotEqualFilter(FilterNotEqual, BaseDateTimeFilter):
    pass


class DateTimeGreaterFilter(FilterGreater, BaseDateTimeFilter):
    pass


class DateTimeSmallerFilter(FilterSmaller, BaseDateTimeFilter):
    pass


class DateTimeBetweenFilter(BaseSQLAFilter, BaseDateTimeBetweenFilter):
    def __init__(self, column_type, column, name, data_type=None, options=None):
        super().__init__(column_type, column, name, "datetimerangepicker", options)

    def apply(self, query, value):
        return query.add_filter(self.column, "between", value)


class DateTimeNotBetweenFilter(DateTimeBetweenFilter):
    def operation(self):
        return lazy_gettext("not between")

    def apply(self, query, value):
        return query.add_filter(self.column, "not_between", value)


class TimeEqualFilter(FilterEqual, BaseTimeFilter):
    pass


class TimeNotEqualFilter(FilterNotEqual, BaseTimeFilter):
    pass


class TimeGreaterFilter(FilterGreater, BaseTimeFilter):
    pass


class TimeSmallerFilter(FilterSmaller, BaseTimeFilter):
    pass


class TimeBetweenFilter(BaseSQLAFilter, BaseTimeBetweenFilter):
    def __init__(self, column_type, column, name, data_type=None, options=None):
        super().__init__(column_type, column, name, "timerangepicker", options)

    def apply(self, query, value):
        return query.add_filter(self.column, "between", value)


class TimeNotBetweenFilter(TimeBetweenFilter):
    def operation(self):
        return lazy_gettext("not between")

    def apply(self, query, value):
        return query.add_filter(self.column, "not_between", value)


class EnumEqualFilter(FilterEqual):
    def __init__(self, column_type, column, name, data_type=None, options=None):
        super().__init__(
            column_type, column, name, data_type, [(v, v) for v in column_type.enums]
        )
        self.enum_class = column_type.enum_class

    def clean(self, value):
        return self.enum_class[value]


class EnumFilterNotEqual(FilterNotEqual):
    def __init__(self, column_type, column, name, data_type=None, options=None):
        super().__init__(
            column_type, column, name, data_type, [(v, v) for v in column_type.enums]
        )
        self.enum_class = column_type.enum_class

    def clean(self, value):
        return self.enum_class[value]


class EnumFilterEmpty(FilterEmpty):
    def __init__(self, column_type, column, name, data_type=None, options=None):
        super().__init__(
            column_type, column, name, data_type, [(v, v) for v in column_type.enums]
        )
        self.enum_class = column_type.enum_class


class EnumFilterInList(FilterInList):
    def __init__(self, column_type, column, name, data_type=None, options=None):
        super().__init__(
            column_type, column, name, data_type, [(v, v) for v in column_type.enums]
        )
        self.enum_class = column_type.enum_class

    def clean(self, value):
        values = super().clean(value)
        values = [self.enum_class[val] for val in values]
        return values


class EnumFilterNotInList(FilterNotInList):
    def __init__(self, column_type, column, name, data_type=None, options=None):
        super().__init__(
            column_type, column, name, data_type, [(v, v) for v in column_type.enums]
        )
        self.enum_class = column_type.enum_class

    def clean(self, value):
        values = super().clean(value)
        values = [self.enum_class[val] for val in values]
        return values


class ChoiceTypeEqualFilter(FilterEqual):
    def apply(self, query, value):
        choice_type = None
        if isinstance(self.column_type.choices, enum.EnumMeta):
            for choice in self.column_type.choices:
                if choice.name == value:
                    choice_type = choice.value
                    break
        else:
            for type, value in self.column_type.choices:
                if value == value:
                    choice_type = type
                    break
        if choice_type:
            return query.add_filter(self.column, "==", choice_type)
        else:
            return query.add_filter(self.column, "==", value)


class ChoiceTypeNotEqualFilter(FilterNotEqual):
    def apply(self, query, value):
        choice_type = None
        if isinstance(self.column_type.choices, enum.EnumMeta):
            for choice in self.column_type.choices:
                if choice.name == value:
                    choice_type = choice.value
                    break
        else:
            for type, value in self.column_type.choices:
                if value == value:
                    choice_type = type
                    break
        if choice_type:
            return query.add_filter(self.column, "!=", choice_type)
        else:
            return query.add_filter(self.column, "!=", value)


class ChoiceTypeLikeFilter(FilterLike):
    def apply(self, query, value):
        choice_type = None
        if isinstance(self.column_type.choices, enum.EnumMeta):
            for choice in self.column_type.choices:
                if choice.name == value:
                    choice_type = choice.value
                    break
        else:
            for type, value in self.column_type.choices:
                if value == value:
                    choice_type = type
                    break
        if choice_type:
            return query.add_filter(self.column, "like", choice_type)
        else:
            return query.add_filter(self.column, "like", value)


class ChoiceTypeNotLikeFilter(FilterNotLike):
    def apply(self, query, value):
        choice_type = None
        if isinstance(self.column_type.choices, enum.EnumMeta):
            for choice in self.column_type.choices:
                if choice.name == value:
                    choice_type = choice.value
                    break
        else:
            for type, value in self.column_type.choices:
                if value == value:
                    choice_type = type
                    break
        if choice_type:
            return query.add_filter(self.column, "not_like", choice_type)
        else:
            return query.add_filter(self.column, "not_like", value)


class FilterConverter(BaseFilterConverter):
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

    @convert_type(
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
    def convert_string(self, column_type, column, name, **kwargs):
        return [f(column_type, column, name, **kwargs) for f in self.string_filters]

    @convert_type("ColorType", "TimezoneType", "CurrencyType")
    def convert_string_key(self, column_type, column, name, **kwargs):
        return [f(column_type, column, name, **kwargs) for f in self.string_key_filters]

    @convert_type("boolean", "tinyint")
    def convert_bool(self, column_type, column, name, **kwargs):
        return [f(column_type, column, name, **kwargs) for f in self.bool_filters]

    @convert_type(
        "int",
        "integer",
        "smallinteger",
        "smallint",
        "biginteger",
        "bigint",
        "mediumint",
    )
    def convert_int(self, column_type, column, name, **kwargs):
        return [f(column_type, column, name, **kwargs) for f in self.int_filters]

    @convert_type("float", "real", "decimal", "numeric", "double_precision", "double")
    def convert_float(self, column_type, column, name, **kwargs):
        return [f(column_type, column, name, **kwargs) for f in self.float_filters]

    @convert_type("date")
    def convert_date(self, column_type, column, name, **kwargs):
        return [f(column_type, column, name, **kwargs) for f in self.date_filters]

    @convert_type("datetime", "datetime2", "timestamp", "smalldatetime")
    def convert_datetime(self, column_type, column, name, **kwargs):
        return [f(column_type, column, name, **kwargs) for f in self.datetime_filters]

    @convert_type("time")
    def convert_time(self, column_type, column, name, **kwargs):
        return [f(column_type, column, name, **kwargs) for f in self.time_filters]

    @convert_type("ChoiceType")
    def convert_choice_type(self, column_type, column, name, **kwargs):
        return [
            f(column_type, column, name, **kwargs) for f in self.choice_type_filters
        ]

    @convert_type("enum")
    def convert_enum(self, column_type, column, name, **kwargs):
        return [f(column_type, column, name, **kwargs) for f in self.enum_filters]
