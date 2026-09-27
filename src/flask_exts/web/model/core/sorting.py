"""Sorting helpers for admin model views.

This module provides sortable-column scaffolding and default ordering helpers
for list-based admin views.
"""

from typing import Optional, Dict, List, Tuple, Union


class SortingMixin:
    """Mixin for sortable-column configuration and ordering logic."""

    column_sortable_list: Optional[List[Union[str, Tuple[str, str]]]] = None
    column_default_sort: Optional[Union[str, Tuple[str, bool], List[Tuple[str, bool]]]] = None

    _sortable_columns: Dict[str, Union[str, List[str]]] = {}

    def scaffold_sortable_columns(self) -> Dict[str, Union[str, List[str]]]:
        """Return a dictionary of sortable columns.

        This method must be implemented by subclasses that need dynamic column
        discovery.

        Returns:
            Dict[str, Union[str, List[str]]]: A mapping of field names to sort
                column names.
        """
        return {}

    def get_sortable_columns(self) -> Dict[str, Union[str, List[str]]]:
        """Return the sortable column mapping for the current view.

        If ``column_sortable_list`` is defined, that mapping is used directly.
        Otherwise, the method falls back to ``scaffold_sortable_columns()``.

        Returns:
            Dict[str, Union[str, List[str]]]: A mapping of column names to
                sortable field names.
        """
        if self.column_sortable_list is None:
            return self.scaffold_sortable_columns() or dict()
        else:
            result = dict()

            for c in self.column_sortable_list:
                if isinstance(c, tuple):
                    result[c[0]] = c[1]
                else:
                    result[c] = c

            return result

    def is_sortable(self, name: str) -> bool:
        """Return whether a column name is sortable.

        Args:
            name: Column name to evaluate.

        Returns:
            bool: ``True`` when the column is sortable, otherwise ``False``.
        """
        return name.lower() in (x.lower() for x in self._sortable_columns)

    def _get_default_order(self) -> Optional[List[Tuple[str, bool]]]:
        """Return the default sort order for the current view.

        Returns:
            Optional[List[Tuple[str, bool]]]: A list of ``(column_name, desc)``
            pairs, or ``None`` when no default ordering is configured.
        """
        if self.column_default_sort:
            if isinstance(self.column_default_sort, list):
                return self.column_default_sort
            elif isinstance(self.column_default_sort, tuple):
                return [self.column_default_sort]
            else:
                return [(self.column_default_sort, False)]

        return None
