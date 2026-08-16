"""
基础字段转换器

提供 SQLAlchemy 字段类型到 WTForms 字段的基础转换功能。
"""

from wtforms import validators
from wtforms.fields import StringField, TextAreaField, IntegerField, DecimalField, BooleanField, DateField
from ...forms.fields import TimeField
from ...forms.widgets import DatePickerWidget


class BasicFieldConverter:
    """
    基础字段类型转换器

    提供基本数据类型（字符串、整数、小数、布尔等）的字段转换。
    """

    def _nullable_common(self, column, field_args, **extra):
        """处理可空列"""
        if column.nullable:
            filters = field_args.get("filters", [])
            filters.append(lambda x: x or None)
            field_args["filters"] = filters

    def _string_common(self, column, field_args, **extra):
        """处理字符串列的通用逻辑"""
        if (
            hasattr(column.type, "length")
            and isinstance(column.type.length, int)
            and column.type.length
        ):
            field_args["validators"].append(validators.Length(max=column.type.length))
        self._nullable_common(column, field_args, **extra)

    def conv_string(self, column, field_args, **extra):
        """转换 String 字段"""
        self._string_common(column=column, field_args=field_args, **extra)
        return StringField(**field_args)

    def conv_text(self, field_args, **extra):
        """转换 Text 字段"""
        self._string_common(field_args=field_args, **extra)
        return TextAreaField(**field_args)

    def conv_boolean(self, field_args, **extra):
        """转换 Boolean 字段"""
        return BooleanField(**field_args)

    def convert_integer(self, column, field_args, **extra):
        """转换 Integer 字段"""
        unsigned = getattr(column.type, "unsigned", False)
        if unsigned:
            field_args["validators"].append(validators.NumberRange(min=0))
        return IntegerField(**field_args)

    def convert_decimal(self, column, field_args, **extra):
        """转换 Decimal/Float 字段"""
        # 使用数据库默认精度而不是 WTForms 默认的
        field_args.setdefault("places", None)
        return DecimalField(**field_args)


class TemporalFieldConverter:
    """
    时间类型字段转换器

    提供日期、时间、日期时间字段的转换。
    """

    def convert_date(self, field_args, **extra):
        """转换 Date 字段"""
        field_args["widget"] = DatePickerWidget()
        return DateField(**field_args)

    def convert_time(self, field_args, **extra):
        """转换 Time 字段"""
        return TimeField(**field_args)

    def convert_datetime(self, field_args, **extra):
        """转换 DateTime 字段"""
        from wtforms.fields import DateTimeLocalField
        return DateTimeLocalField(**field_args)


class SpecialFieldConverter:
    """
    特殊类型字段转换器

    提供枚举、JSON 等特殊字段的转换。
    """

    def convert_enum(self, column, field_args, **extra):
        """转换 Enum 字段"""
        from enum import Enum
        from ...forms.fields import Select2Field

        available_choices = [(f, f) for f in column.type.enums]
        accepted_values = [choice[0] for choice in available_choices]

        if column.nullable:
            field_args["allow_blank"] = column.nullable
            accepted_values.append(None)

        field_args["choices"] = available_choices
        field_args["validators"].append(validators.AnyOf(accepted_values))
        field_args["coerce"] = lambda v: v.name if isinstance(v, Enum) else str(v)
        return Select2Field(**field_args)

    def convert_json(self, field_args, **extra):
        """转换 JSON 字段"""
        from ...forms.fields import JSONField
        return JSONField(**field_args)
