"""Value extraction and formatting helpers for admin model views.

This module resolves nested model attributes, applies custom formatters, and
handles choice mappings for list, detail, and export views.
"""

from collections.abc import Callable
from functools import reduce
from typing import Any


class ValuesMixin:
    """Mixin for retrieving and formatting display values in admin views."""

    column_formatters: dict[str, Callable] = {}
    """Column-specific formatters used in list views."""

    column_formatters_export: dict[str, Callable] | None = None
    """Column-specific formatters used during export."""

    column_formatters_detail: dict[str, Callable] | None = None
    """Column-specific formatters used in detail views."""

    column_type_formatters: dict[type, Callable] | None = None
    """Type-based formatters used in list views."""

    column_type_formatters_export: dict[type, Callable] | None = None
    """Type-based formatters used during export."""

    column_type_formatters_detail: dict[type, Callable] | None = None
    """Type-based formatters used in detail views."""

    column_choices: dict[str, dict[Any, str]] = {}
    """Choice mappings keyed by column name."""

    def _get_object_attr(self, obj: Any, name: str) -> Any:
        """Resolve a nested attribute from an object.

        Args:
            obj: Model instance or object to read from.
            name: Dot-delimited attribute path such as ``user.username``.

        Returns:
            Any: The resolved attribute value.

        Raises:
            AttributeError: If the attribute path does not exist.
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
        column_fmt = column_formatters.get(name)
        if column_fmt is not None:
            value = column_fmt(self, model, name)
        else:
            value = self._get_object_attr(model, name)

        choices_map = self.column_choices.get(name, {})
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
        column_type_formatters = self.column_type_formatters or {}

        return self._get_format_value(
            model,
            name,
            self.column_formatters,
            column_type_formatters,
        )

    def get_detail_value(self, model: Any, name: str) -> Any:
        """Return the value displayed in the detail view.

        Args:
            model: Model instance.
            name: Field name.

        Returns:
            Any: The formatted value.
        """
        column_formatters_detail = (
            self.column_formatters_detail or self.column_formatters
        )
        column_type_formatters_detail = (
            self.column_type_formatters_detail or self.column_type_formatters or {}
        )

        return self._get_format_value(
            model,
            name,
            column_formatters_detail,
            column_type_formatters_detail,
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
        column_formatters_export = (
            self.column_formatters_export or self.column_formatters
        )
        column_type_formatters_export = (
            self.column_type_formatters_export or self.column_type_formatters or {}
        )

        return self._get_format_value(
            model,
            name,
            column_formatters_export,
            column_type_formatters_export,
        )

    def get_export_name(self, export_type: str = "csv") -> str:
        """Return the generated export filename.

        Args:
            export_type: Export format name, for example ``csv``.

        Returns:
            str: Export filename.
        """
        import time

        filename = "{}_{}.{}".format(self.name,time.strftime("%Y-%m-%d_%H-%M-%S"),export_type)

        return filename
