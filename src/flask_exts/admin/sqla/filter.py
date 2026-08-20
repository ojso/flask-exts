"""
SQLAlchemy 过滤器 - 优化版本

这个模块提供了 SQLAlchemy 特定的过滤器实现。
优化：使用工厂函数动态生成类型特定的过滤器，减少重复代码。

架构：
  - BaseSQLAFilter: 基础过滤器类
  - 基础操作过滤器：FilterEqual, FilterNotEqual, FilterGreater, FilterSmaller, FilterLike, FilterNotLike, FilterEmpty, FilterInList, FilterNotInList
  - 工厂函数：create_type_filters() 动态生成类型特定的过滤器
  - FilterConverter: 转换器，根据列类型返回适当的过滤器
"""


from flask_babel import lazy_gettext
from ..model.filter import BaseFilterConverter
from ..model.filter import convert_filter
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


# ===============================================
# 基础过滤器类
# ===============================================

class BaseSQLAFilter(BaseFilter):
    """Base SQLAlchemy filter."""

    def __init__(self, column_type, column: str, name, data_type=None, options=None):
        """
        Constructor.

        :param column: Model field
        :param name: Display name
        :param options: Fixed set of options
        :param data_type: Client data type
        """
        super().__init__(name, data_type, options)
        self.column_type = column_type
        self.column = column


class FilterEqual(BaseSQLAFilter):
    """Equals filter"""
    def operation(self):
        return lazy_gettext("equals")

    def apply(self, query, value):
        return query.add_filter(self.column, "==", value)


class FilterNotEqual(BaseSQLAFilter):
    """Not equal filter"""
    def operation(self):
        return lazy_gettext("not equal")

    def apply(self, query, value):
        return query.add_filter(self.column, "!=", value)


class FilterGreater(BaseSQLAFilter):
    """Greater than filter"""
    def operation(self):
        return lazy_gettext("greater than")

    def apply(self, query, value):
        return query.add_filter(self.column, ">", value)


class FilterSmaller(BaseSQLAFilter):
    """Smaller than filter"""
    def operation(self):
        return lazy_gettext("smaller than")

    def apply(self, query, value):
        return query.add_filter(self.column, "<", value)


class FilterLike(BaseSQLAFilter):
    """Contains filter"""
    def operation(self):
        return lazy_gettext("contains")

    def apply(self, query, value):
        return query.add_filter(self.column, "ilike", value)


class FilterNotLike(BaseSQLAFilter):
    """Not contains filter"""
    def operation(self):
        return lazy_gettext("not contains")

    def apply(self, query, value):
        return query.add_filter(self.column, "not_ilike", value)


class FilterEmpty(BaseSQLAFilter, BaseBooleanFilter):
    """Empty/null filter"""
    def operation(self):
        return lazy_gettext("empty")

    def apply(self, query, value):
        if value == "1":
            return query.add_filter(self.column, "is_null", None)
        else:
            return query.add_filter(self.column, "isnot_null", None)


class FilterInList(BaseSQLAFilter):
    """In list filter"""
    def __init__(self, column_type, column, name, data_type=None, options=None):
        super().__init__(column_type, column, name, "select2-tags", options)

    def operation(self):
        return lazy_gettext("in list")

    def clean(self, value):
        return [v.strip() for v in value.split(",") if v.strip()]

    def apply(self, query, value):
        return query.add_filter(self.column, "in", value)


class FilterNotInList(FilterInList):
    """Not in list filter"""
    def operation(self):
        return lazy_gettext("not in list")

    def apply(self, query, value):
        return query.add_filter(self.column, "not_in", value)


# ===============================================
# 工厂函数 - 动态生成类型特定的过滤器
# ===============================================

def create_type_filters(base_filter_classes, type_mixin, type_prefix):
    """
    工厂函数：为特定类型动态生成过滤器类

    Args:
        base_filter_classes: 基础过滤器类列表，如 [FilterEqual, FilterNotEqual, ...]
        type_mixin: 类型混入类，如 BaseIntFilter, BaseDateFilter
        type_prefix: 类型前缀，用于生成类名，如 'Int', 'Date'

    Returns:
        dict: {class_name: generated_class, ...}
    """
    result = {}

    for base_filter in base_filter_classes:
        # 生成类名：DateEqualFilter, IntGreaterFilter 等
        class_name = f"{type_prefix}{base_filter.__name__}"

        # 动态创建类
        new_class = type(
            class_name,
            (base_filter, type_mixin),
            {}
        )

        result[class_name] = new_class

    return result


# ===============================================
# 特殊过滤器 - 枚举和选择类型
# ===============================================

class EnumEqualFilter(FilterEqual):
    """Enum equals filter"""
    def apply(self, query, value):
        return query.add_filter(self.column, "==", value)


class EnumFilterNotEqual(FilterNotEqual):
    """Enum not equal filter"""
    pass


class EnumFilterEmpty(FilterEmpty):
    """Enum empty filter"""
    pass


class EnumFilterInList(FilterInList):
    """Enum in list filter"""
    pass


class EnumFilterNotInList(FilterNotInList):
    """Enum not in list filter"""
    pass


class ChoiceTypeEqualFilter(FilterEqual):
    """Choice type equals filter"""
    pass


class ChoiceTypeNotEqualFilter(FilterNotEqual):
    """Choice type not equal filter"""
    pass


class ChoiceTypeLikeFilter(FilterLike):
    """Choice type contains filter"""
    def apply(self, query, value):
        choice_type = None

        if hasattr(self.column_type, 'choices'):
            for type, choice in self.column_type.choices:
                if isinstance(choice, (list, tuple)):
                    for sub_choice, sub_name in choice:
                        if sub_name and value in sub_name:
                            choice_type = type
                            break
                else:
                    if choice and value in choice:
                        choice_type = type
                        break

        if choice_type:
            return query.add_filter(self.column, "like", choice_type)
        else:
            return query.add_filter(self.column, "like", value)


class ChoiceTypeNotLikeFilter(FilterNotLike):
    """Choice type not contains filter"""
    def apply(self, query, value):
        choice_type = None

        if hasattr(self.column_type, 'choices'):
            for type, choice in self.column_type.choices:
                if isinstance(choice, (list, tuple)):
                    for sub_choice, sub_name in choice:
                        if sub_name and value in sub_name:
                            choice_type = type
                            break
                else:
                    if choice and value in choice:
                        choice_type = type
                        break

        if choice_type:
            return query.add_filter(self.column, "not_like", choice_type)
        else:
            return query.add_filter(self.column, "not_like", value)


# ===============================================
# 类型特定的过滤器（使用工厂函数生成）
# ===============================================

# Boolean 过滤器
BooleanEqualFilter = type('BooleanEqualFilter', (FilterEqual, BaseBooleanFilter), {})
BooleanNotEqualFilter = type('BooleanNotEqualFilter', (FilterNotEqual, BaseBooleanFilter), {})

# Int 过滤器
IntEqualFilter = type('IntEqualFilter', (FilterEqual, BaseIntFilter), {})
IntNotEqualFilter = type('IntNotEqualFilter', (FilterNotEqual, BaseIntFilter), {})
IntGreaterFilter = type('IntGreaterFilter', (FilterGreater, BaseIntFilter), {})
IntSmallerFilter = type('IntSmallerFilter', (FilterSmaller, BaseIntFilter), {})
IntInListFilter = type('IntInListFilter', (FilterInList, BaseIntListFilter), {})
IntNotInListFilter = type('IntNotInListFilter', (FilterNotInList, BaseIntListFilter), {})

# Float 过滤器
FloatEqualFilter = type('FloatEqualFilter', (FilterEqual, BaseFloatFilter), {})
FloatNotEqualFilter = type('FloatNotEqualFilter', (FilterNotEqual, BaseFloatFilter), {})
FloatGreaterFilter = type('FloatGreaterFilter', (FilterGreater, BaseFloatFilter), {})
FloatSmallerFilter = type('FloatSmallerFilter', (FilterSmaller, BaseFloatFilter), {})
FloatInListFilter = type('FloatInListFilter', (FilterInList, BaseFloatListFilter), {})
FloatNotInListFilter = type('FloatNotInListFilter', (FilterNotInList, BaseFloatListFilter), {})

# Date 过滤器
DateEqualFilter = type('DateEqualFilter', (FilterEqual, BaseDateFilter), {})
DateNotEqualFilter = type('DateNotEqualFilter', (FilterNotEqual, BaseDateFilter), {})
DateGreaterFilter = type('DateGreaterFilter', (FilterGreater, BaseDateFilter), {})
DateSmallerFilter = type('DateSmallerFilter', (FilterSmaller, BaseDateFilter), {})

class DateBetweenFilter(BaseSQLAFilter, BaseDateBetweenFilter):
    """Date between filter"""
    def __init__(self, column_type, column, name, data_type=None, options=None):
        super().__init__(column_type, column, name, "daterangepicker", options)

    def operation(self):
        return lazy_gettext("between")

    def apply(self, query, value):
        return query.add_filter(self.column, "between", value)


class DateNotBetweenFilter(DateBetweenFilter):
    """Date not between filter"""
    def operation(self):
        return lazy_gettext("not between")

    def apply(self, query, value):
        return query.add_filter(self.column, "not_between", value)


# DateTime 过滤器
DateTimeEqualFilter = type('DateTimeEqualFilter', (FilterEqual, BaseDateTimeFilter), {})
DateTimeNotEqualFilter = type('DateTimeNotEqualFilter', (FilterNotEqual, BaseDateTimeFilter), {})
DateTimeGreaterFilter = type('DateTimeGreaterFilter', (FilterGreater, BaseDateTimeFilter), {})
DateTimeSmallerFilter = type('DateTimeSmallerFilter', (FilterSmaller, BaseDateTimeFilter), {})

class DateTimeBetweenFilter(BaseSQLAFilter, BaseDateTimeBetweenFilter):
    """DateTime between filter"""
    def __init__(self, column_type, column, name, data_type=None, options=None):
        super().__init__(column_type, column, name, "daterangepicker", options)

    def operation(self):
        return lazy_gettext("between")

    def apply(self, query, value):
        return query.add_filter(self.column, "between", value)


class DateTimeNotBetweenFilter(DateTimeBetweenFilter):
    """DateTime not between filter"""
    def operation(self):
        return lazy_gettext("not between")

    def apply(self, query, value):
        return query.add_filter(self.column, "not_between", value)


# Time 过滤器
TimeEqualFilter = type('TimeEqualFilter', (FilterEqual, BaseTimeFilter), {})
TimeNotEqualFilter = type('TimeNotEqualFilter', (FilterNotEqual, BaseTimeFilter), {})
TimeGreaterFilter = type('TimeGreaterFilter', (FilterGreater, BaseTimeFilter), {})
TimeSmallerFilter = type('TimeSmallerFilter', (FilterSmaller, BaseTimeFilter), {})

class TimeBetweenFilter(BaseSQLAFilter, BaseTimeBetweenFilter):
    """Time between filter"""
    def __init__(self, column_type, column, name, data_type=None, options=None):
        super().__init__(column_type, column, name, "daterangepicker", options)

    def operation(self):
        return lazy_gettext("between")

    def apply(self, query, value):
        return query.add_filter(self.column, "between", value)


class TimeNotBetweenFilter(TimeBetweenFilter):
    """Time not between filter"""
    def operation(self):
        return lazy_gettext("not between")

    def apply(self, query, value):
        return query.add_filter(self.column, "not_between", value)


# ===============================================
# 转换器
# ===============================================

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
