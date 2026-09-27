"""Field conversion helpers for mapping SQLAlchemy columns to WTForms fields."""

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
    """Convert common scalar SQLAlchemy types into WTForms fields."""

    def _nullable_common(self, column, field_args, **extra):
        """Normalize nullable values so ``None`` is preserved."""
        if column.nullable:
            filters = field_args.get("filters", [])
            filters.append(lambda x: x or None)
            field_args["filters"] = filters

    def _string_common(self, column, field_args, **extra):
        """Apply common validation for string-like columns."""
        if (
            hasattr(column.type, "length")
            and isinstance(column.type.length, int)
            and column.type.length
        ):
            field_args["validators"].append(validators.Length(max=column.type.length))
        self._nullable_common(column, field_args, **extra)

    @convert_form_field("String")
    def conv_string(self, column, field_args, **extra):
        """Convert a string column to a WTForms StringField."""
        self._string_common(column=column, field_args=field_args, **extra)
        return StringField(**field_args)

    @convert_form_field("Text")
    def conv_text(self, field_args, **extra):
        """Convert a text column to a WTForms TextAreaField."""
        self._string_common(field_args=field_args, **extra)
        return TextAreaField(**field_args)

    @convert_form_field("Boolean")
    def conv_boolean(self, field_args, **extra):
        """Convert a Boolean column to a WTForms BooleanField."""
        return BooleanField(**field_args)

    @convert_form_field("Integer", "BigInteger", "SmallInteger")
    def convert_integer(self, column, field_args, **extra):
        """Convert integer columns to a WTForms IntegerField."""
        unsigned = getattr(column.type, "unsigned", False)
        if unsigned:
            field_args["validators"].append(validators.NumberRange(min=0))
        return IntegerField(**field_args)

    @convert_form_field("Numeric", "DECIMAL", "Float", "REAL", "DOUBLE")
    def convert_decimal(self, column, field_args, **extra):
        """Convert numeric columns to a WTForms DecimalField."""
        field_args.setdefault("places", None)
        return DecimalField(**field_args)


class TemporalFieldConverter:
    """Convert date, time, and datetime columns to the appropriate WTForms fields."""

    @convert_form_field("Date")
    def convert_date(self, field_args, **extra):
        """Convert a date column to a WTForms DateField."""
        field_args["widget"] = DatePickerWidget()
        return DateField(**field_args)

    @convert_form_field("Time")
    def convert_time(self, field_args, **extra):
        """Convert a time column to a WTForms TimeField."""
        return TimeField(**field_args)

    @convert_form_field("DateTime", "TIMESTAMP")
    def convert_datetime(self, field_args, **extra):
        """Convert a datetime column to a WTForms DateTimeLocalField."""
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
        """Convert a JSON column to a JSON-capable form field."""
        from ....forms.fields import JSONField

        return JSONField(**field_args)
