"""
Basic field converters / 基础字段转换器

English summary: This module converts SQLAlchemy column types to WTForms field definitions and provides reusable conversion helpers.
中文说明：提供 SQLAlchemy 字段类型到 WTForms 字段的基础转换功能。
"""

import types
from wtforms import validators
from wtforms.fields import (
    StringField,
    TextAreaField,
    IntegerField,
    DecimalField,
    BooleanField,
    DateField,
)
from ....forms.fields import TimeField
from ....forms.widgets import DatePickerWidget


def convert_form_field(*args):
    def decorator(func):
        func._converter_for_form_field = args
        return func

    return decorator


class BaseFormFieldConverter:
    _converters = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        converters = {}
        # Merge converters from base classes
        for base in cls.__bases__:
            base_map = getattr(base, "_converters", {})
            converters.update(base_map)
        # Add converters from the current class including methods from the entire MRO
        # for name, method in cls.__dict__.items(): # only check the current class, not the base classes
        for base in cls.__mro__:
            for name, method in base.__dict__.items():
                if callable(method) and hasattr(method, "_converter_for_form_field"):
                    for type_name in method._converter_for_form_field:
                        converters[type_name] = method
        cls._converters = converters

    def __init__(self, use_mro=True):
        self.use_mro = use_mro

    def get_converter(self, column):
        col_type = type(column.type)
        if self.use_mro:
            types_list = col_type.__mro__
        else:
            types_list = (col_type,)

        # Search by module + name
        for t in types_list:
            full_name = f"{t.__module__}.{t.__name__}"
            if full_name in self._converters:
                func = self._converters[full_name]
                return types.MethodType(func, self)

        # Search by name
        for t in types_list:
            short_name = t.__name__
            if short_name in self._converters:
                func = self._converters[short_name]
                return types.MethodType(func, self)

        return None

    def get_form(self, model, base_class, only=None, exclude=None, field_args=None):
        raise NotImplementedError()


class BasicFieldConverter:
    """
    Basic field type converter / 基础字段类型转换器

    English summary: Converts common scalar types such as strings, integers, decimals, and booleans to WTForms fields.
    中文说明：提供基本数据类型（字符串、整数、小数、布尔等）的字段转换。
    """

    def _nullable_common(self, column, field_args, **extra):
        """English: comment / 处理可空列"""
        if column.nullable:
            filters = field_args.get("filters", [])
            filters.append(lambda x: x or None)
            field_args["filters"] = filters

    def _string_common(self, column, field_args, **extra):
        """English: comment / 处理字符串列的通用逻辑"""
        if (
            hasattr(column.type, "length")
            and isinstance(column.type.length, int)
            and column.type.length
        ):
            field_args["validators"].append(validators.Length(max=column.type.length))
        self._nullable_common(column, field_args, **extra)

    @convert_form_field("String")
    def conv_string(self, column, field_args, **extra):
        """English: convert String field / 转换 String 字段"""
        self._string_common(column=column, field_args=field_args, **extra)
        return StringField(**field_args)

    @convert_form_field("Text")
    def conv_text(self, field_args, **extra):
        """English: convert Text field / 转换 Text 字段"""
        self._string_common(field_args=field_args, **extra)
        return TextAreaField(**field_args)

    @convert_form_field("Boolean")
    def conv_boolean(self, field_args, **extra):
        """English: convert Boolean field / 转换 Boolean 字段"""
        return BooleanField(**field_args)

    @convert_form_field("Integer", "BigInteger", "SmallInteger")
    def convert_integer(self, column, field_args, **extra):
        """English: convert Integer field / 转换 Integer 字段"""
        unsigned = getattr(column.type, "unsigned", False)
        if unsigned:
            field_args["validators"].append(validators.NumberRange(min=0))
        return IntegerField(**field_args)

    @convert_form_field("Numeric", "DECIMAL", "Float", "REAL", "DOUBLE")
    def convert_decimal(self, column, field_args, **extra):
        """English: convert Decimal Float field / 转换 Decimal/Float 字段"""
        # override default decimal places limit, use database defaults instead
        field_args.setdefault("places", None)
        return DecimalField(**field_args)


class TemporalFieldConverter:
    """
    Temporal field converter / 时间类型字段转换器

    English summary: Converts date, time, and datetime fields to appropriate WTForms input fields.
    中文说明：提供日期、时间、日期时间字段的转换。
    """

    @convert_form_field("Date")
    def convert_date(self, field_args, **extra):
        """English: convert Date field / 转换 Date 字段"""
        field_args["widget"] = DatePickerWidget()
        return DateField(**field_args)

    @convert_form_field("Time")
    def convert_time(self, field_args, **extra):
        """English: convert Time field / 转换 Time 字段"""
        return TimeField(**field_args)

    @convert_form_field("DateTime", "TIMESTAMP")
    def convert_datetime(self, field_args, **extra):
        """English: convert DateTime field / 转换 DateTime 字段"""
        from wtforms.fields import DateTimeLocalField

        return DateTimeLocalField(**field_args)


class SpecialFieldConverter:
    """
    Special field converter.
    Converts enum and JSON-like fields to compatible WTForms widgets and field types.
    """

    @convert_form_field("Enum")
    def convert_enum(self, column, field_args, **extra):
        """convert Enum field"""
        from enum import Enum
        from ....forms.fields import Select2Field

        available_choices = [(f, f) for f in column.type.enums]
        accepted_values = [choice[0] for choice in available_choices]

        if column.nullable:
            field_args["allow_blank"] = column.nullable
            accepted_values.append(None)

        field_args["choices"] = available_choices
        field_args["validators"].append(validators.AnyOf(accepted_values))
        field_args["coerce"] = lambda v: v.name if isinstance(v, Enum) else str(v)
        return Select2Field(**field_args)

    @convert_form_field("JSON")
    def convert_json(self, field_args, **extra):
        """English: convert JSON field / 转换 JSON 字段"""
        from ....forms.fields import JSONField

        return JSONField(**field_args)
