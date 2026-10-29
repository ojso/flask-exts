"""Value extraction and formatting helpers for admin model views.

This module resolves nested model attributes, applies custom formatters, and
handles choice mappings for list, detail, and export views.
"""

from collections.abc import Callable
from functools import reduce
from typing import Any

from ..type_formatters import BASE_FORMATTERS, DETAIL_FORMATTERS, EXPORT_FORMATTERS


class ValueHandler:
    """Handler for retrieving and formatting display values in admin views."""

    def __init__(self, view):
        self.view = view
        self.column_formatters = view.column_formatters
        self.column_formatters_detail = (
            view.column_formatters_detail or self.column_formatters
        )
        self.column_formatters_export = (
            view.column_formatters_export or self.column_formatters
        )
        self.column_type_formatters = view.column_type_formatters or BASE_FORMATTERS
        self.column_type_formatters_export = (
            view.column_type_formatters_export or EXPORT_FORMATTERS
        )
        self.column_type_formatters_detail = (
            view.column_type_formatters_detail or DETAIL_FORMATTERS
        )

    def _get_object_attr(self, obj: Any, name: str) -> Any:
        """Resolve a nested attribute from an object.

        Args:
            obj: Model instance or object to read from.
            name: Dot-delimited attribute path such as ``user.username``.

        Returns:
            Any: The resolved attribute value.
        """
        return reduce(getattr, name.split("."), obj)

    def _get_format_value(
        self,
        model: Any,
        name: str,
        column_formatters: dict[str, Callable],
        column_type_formatters: dict[type, Callable] | None,
    ) -> Any:
        """Return the display value for a model field.

        The value is processed in the following order: column formatter,
        choice mapping, and finally the type formatter.

        Args:
            model: Model instance.
            name: Field name.
            column_formatters: Column-specific formatter mapping.
            column_type_formatters: Type-based formatter mapping.

        Returns:
            Any: The formatted value.
        """

        if column_formatters is not None:
            column_fmt = column_formatters.get(name)
        else:
            column_fmt = None

        if column_fmt is not None:
            value = column_fmt(self, model, name)
        else:
            value = self._get_object_attr(model, name)

        if self.view.column_choices is not None:
            choices_map = self.view.column_choices.get(name)
            if choices_map:
                return choices_map.get(value) or value

        if column_type_formatters:
            type_fmt = None
            for typeobj, formatter in column_type_formatters.items():
                if isinstance(value, typeobj):
                    type_fmt = formatter
                    break
            if type_fmt is not None:
                value = type_fmt(self, value, name)

        return value

    def get_list_value(self, model: Any, name: str) -> Any:
        """Return the value displayed in the list view.

        Args:
            model: Model instance.
            name: Field name.

        Returns:
            Any: The formatted value.
        """
        return self._get_format_value(
            model,
            name,
            self.column_formatters,
            self.column_type_formatters,
        )

    def get_detail_value(self, model: Any, name: str) -> Any:
        """Return the value displayed in the detail view.

        Args:
            model: Model instance.
            name: Field name.

        Returns:
            Any: The formatted value.
        """

        return self._get_format_value(
            model,
            name,
            self.column_formatters_detail,
            self.column_type_formatters_detail,
        )

    def get_export_value(self, model: Any, name: str) -> Any:
        """Return the value used in export output.

        This allows the export pipeline to use a formatter configuration different
        from the HTML list or detail views.

        Args:
            model: Model instance.
            name: Field name.

        Returns:
            Any: The formatted value.
        """

        return self._get_format_value(
            model,
            name,
            self.column_formatters_export,
            self.column_type_formatters_export,
        )
