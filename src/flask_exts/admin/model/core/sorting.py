class SortingMixin:
    """Mixin for sortable-column configuration and ordering logic."""

    column_sortable_list: list[str | tuple[str, str]] | None = None
    column_default_sort: str | tuple[str, bool] | list[tuple[str, bool]] | None = None

    _sortable_columns: dict[str, str | list[str]] = {}

    def scaffold_sortable_columns(self) -> dict[str, str | list[str]]:
        """Return a dictionary of sortable columns.

        This method must be implemented by subclasses that need dynamic column discovery.

        Returns:
            dict[str, str | list[str]]: A mapping of field names to sort column names.
        """
        return {}

    def get_sortable_columns(self) -> dict[str, str | list[str]]:
        """Return the sortable column mapping for the current view.

        If ``column_sortable_list`` is defined, that mapping is used directly.
        Otherwise, the method falls back to ``scaffold_sortable_columns()``.

        Returns:
            dict[str, str | list[str]]: A mapping of column names to
                sortable field names.
        """
        if self.column_sortable_list is None:
            return self.scaffold_sortable_columns() or {}
        else:
            result = {}

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
        return name in self._sortable_columns

    def _get_default_order(self) -> list[tuple[str, bool]] | None:
        """Return the default sort order for the current view.

        Returns:
            list[tuple[str, bool]] | None: A list of ``(column_name, desc)``
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
