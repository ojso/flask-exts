"""SQLAlchemy-specific filter implementations.

This module provides filter primitives for SQLAlchemy-backed models and uses a
factory pattern to generate type-specific filter classes with minimal duplicated
logic.

The module contains:

- BaseSQLAFilter: the base filter class.
- FilterEqual, FilterNotEqual, FilterGreater, FilterSmaller, FilterLike,
  FilterNotLike, FilterEmpty, FilterInList, and FilterNotInList: concrete
  filter operations.
- create_type_filters(): factory for generating type-specific filters.
- FilterConverter: conversion logic that maps column types to the appropriate
  filter class.
"""

from flask_babel import lazy_gettext

from ...model.filter import (
    BaseBooleanFilter,
    BaseDateBetweenFilter,
    BaseDateFilter,
    BaseDateTimeBetweenFilter,
    BaseDateTimeFilter,
    BaseFilter,
    BaseFloatFilter,
    BaseFloatListFilter,
    BaseIntFilter,
    BaseIntListFilter,
    BaseTimeBetweenFilter,
    BaseTimeFilter,
)

# Base SQLAlchemy filter class.


class BaseSQLAFilter(BaseFilter):
    """Base SQLAlchemy filter."""

    def __init__(self, column_type, column: str, name, data_type=None, options=None):
        """
        Constructor.

        Args:
            column: Model field
            name: Display name
            options: Fixed set of options
            data_type: Client data type
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
        super().__init__(column_type, column, name, "text", options)

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


# Factory for dynamically generating type-specific filters.


def create_type_filters(base_filter_classes, type_mixin, type_prefix):
    """Create generated filter classes for a specific type.

    Args:
        base_filter_classes: Base filter classes such as
            ``[FilterEqual, FilterNotEqual, ...]``.
        type_mixin: Type mixin such as ``BaseIntFilter`` or ``BaseDateFilter``.
        type_prefix: Prefix used to build generated class names.

    Returns:
        dict: A mapping of generated class names to classes.
    """
    result = {}

    for base_filter in base_filter_classes:
        class_name = f"{type_prefix}{base_filter.__name__}"

        new_class = type(class_name, (base_filter, type_mixin), {})

        result[class_name] = new_class

    return result


# Specialized filters for enum and choice-column types.


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

        if hasattr(self.column_type, "choices"):
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

        if hasattr(self.column_type, "choices"):
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


# Type-specific filters generated via the factory pattern.

BooleanEqualFilter = type("BooleanEqualFilter", (FilterEqual, BaseBooleanFilter), {})
BooleanNotEqualFilter = type(
    "BooleanNotEqualFilter", (FilterNotEqual, BaseBooleanFilter), {}
)

IntEqualFilter = type("IntEqualFilter", (FilterEqual, BaseIntFilter), {})
IntNotEqualFilter = type("IntNotEqualFilter", (FilterNotEqual, BaseIntFilter), {})
IntGreaterFilter = type("IntGreaterFilter", (FilterGreater, BaseIntFilter), {})
IntSmallerFilter = type("IntSmallerFilter", (FilterSmaller, BaseIntFilter), {})
IntInListFilter = type("IntInListFilter", (FilterInList, BaseIntListFilter), {})
IntNotInListFilter = type(
    "IntNotInListFilter", (FilterNotInList, BaseIntListFilter), {}
)

FloatEqualFilter = type("FloatEqualFilter", (FilterEqual, BaseFloatFilter), {})
FloatNotEqualFilter = type("FloatNotEqualFilter", (FilterNotEqual, BaseFloatFilter), {})
FloatGreaterFilter = type("FloatGreaterFilter", (FilterGreater, BaseFloatFilter), {})
FloatSmallerFilter = type("FloatSmallerFilter", (FilterSmaller, BaseFloatFilter), {})
FloatInListFilter = type("FloatInListFilter", (FilterInList, BaseFloatListFilter), {})
FloatNotInListFilter = type(
    "FloatNotInListFilter", (FilterNotInList, BaseFloatListFilter), {}
)

DateEqualFilter = type("DateEqualFilter", (FilterEqual, BaseDateFilter), {})
DateNotEqualFilter = type("DateNotEqualFilter", (FilterNotEqual, BaseDateFilter), {})
DateGreaterFilter = type("DateGreaterFilter", (FilterGreater, BaseDateFilter), {})
DateSmallerFilter = type("DateSmallerFilter", (FilterSmaller, BaseDateFilter), {})


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


DateTimeEqualFilter = type("DateTimeEqualFilter", (FilterEqual, BaseDateTimeFilter), {})
DateTimeNotEqualFilter = type(
    "DateTimeNotEqualFilter", (FilterNotEqual, BaseDateTimeFilter), {}
)
DateTimeGreaterFilter = type(
    "DateTimeGreaterFilter", (FilterGreater, BaseDateTimeFilter), {}
)
DateTimeSmallerFilter = type(
    "DateTimeSmallerFilter", (FilterSmaller, BaseDateTimeFilter), {}
)


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


TimeEqualFilter = type("TimeEqualFilter", (FilterEqual, BaseTimeFilter), {})
TimeNotEqualFilter = type("TimeNotEqualFilter", (FilterNotEqual, BaseTimeFilter), {})
TimeGreaterFilter = type("TimeGreaterFilter", (FilterGreater, BaseTimeFilter), {})
TimeSmallerFilter = type("TimeSmallerFilter", (FilterSmaller, BaseTimeFilter), {})


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
