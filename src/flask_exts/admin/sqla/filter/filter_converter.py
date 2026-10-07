from ...model.filter import BaseFilterConverter, convert_filter
from .filters import (
    # bool_filters
    BooleanEqualFilter,
    BooleanNotEqualFilter,
    # choice_type_filters
    ChoiceTypeEqualFilter,
    ChoiceTypeLikeFilter,
    ChoiceTypeNotEqualFilter,
    ChoiceTypeNotLikeFilter,
    DateBetweenFilter,
    # date_filters
    DateEqualFilter,
    DateGreaterFilter,
    DateNotBetweenFilter,
    DateNotEqualFilter,
    DateSmallerFilter,
    DateTimeBetweenFilter,
    # datetime_filters
    DateTimeEqualFilter,
    DateTimeGreaterFilter,
    DateTimeNotBetweenFilter,
    DateTimeNotEqualFilter,
    DateTimeSmallerFilter,
    # enum_filters
    EnumEqualFilter,
    EnumFilterEmpty,
    EnumFilterInList,
    EnumFilterNotEqual,
    EnumFilterNotInList,
    FilterEmpty,
    # string_key_filters
    FilterEqual,
    FilterInList,
    # string_filters
    FilterLike,
    FilterNotEqual,
    FilterNotInList,
    FilterNotLike,
    # float_filters
    FloatEqualFilter,
    FloatGreaterFilter,
    FloatInListFilter,
    FloatNotEqualFilter,
    FloatNotInListFilter,
    FloatSmallerFilter,
    # int_filters
    IntEqualFilter,
    IntGreaterFilter,
    IntInListFilter,
    IntNotEqualFilter,
    IntNotInListFilter,
    IntSmallerFilter,
    TimeBetweenFilter,
    # time_filters
    TimeEqualFilter,
    TimeGreaterFilter,
    TimeNotBetweenFilter,
    TimeNotEqualFilter,
    TimeSmallerFilter,
)


class FilterConverter(BaseFilterConverter):
    """SQLAlchemy filter converter"""

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

    @convert_filter(
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

    @convert_filter("ColorType", "TimezoneType", "CurrencyType")
    def convert_string_key(self, column_type, column, name, **kwargs):
        return [f(column_type, column, name, **kwargs) for f in self.string_key_filters]

    @convert_filter("boolean", "tinyint")
    def convert_bool(self, column_type, column, name, **kwargs):
        return [f(column_type, column, name, **kwargs) for f in self.bool_filters]

    @convert_filter(
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

    @convert_filter("float", "real", "decimal", "numeric", "double_precision", "double")
    def convert_float(self, column_type, column, name, **kwargs):
        return [f(column_type, column, name, **kwargs) for f in self.float_filters]

    @convert_filter("date")
    def convert_date(self, column_type, column, name, **kwargs):
        return [f(column_type, column, name, **kwargs) for f in self.date_filters]

    @convert_filter("datetime", "datetime2", "timestamp", "smalldatetime")
    def convert_datetime(self, column_type, column, name, **kwargs):
        return [f(column_type, column, name, **kwargs) for f in self.datetime_filters]

    @convert_filter("time")
    def convert_time(self, column_type, column, name, **kwargs):
        return [f(column_type, column, name, **kwargs) for f in self.time_filters]

    @convert_filter("ChoiceType")
    def convert_choice_type(self, column_type, column, name, **kwargs):
        return [
            f(column_type, column, name, **kwargs) for f in self.choice_type_filters
        ]

    @convert_filter("enum")
    def convert_enum(self, column_type, column, name, **kwargs):
        return [f(column_type, column, name, **kwargs) for f in self.enum_filters]
