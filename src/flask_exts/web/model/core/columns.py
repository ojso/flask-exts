from typing import Optional, Tuple, List, Dict, Any


class ColumnsMixin:
    """ 
    Columns Manager
    """
    column_list: Optional[List[str]] = None
    """
        Collection of the model field names for the list view.
        If set to `None`, will get them from the model.

        For example::

            class MyModelView(BaseModelView):
                column_list = ('name', 'last_name', 'email')

        SQLAlchemy model attributes can be used instead of strings::

            class MyModelView(BaseModelView):
                column_list = ('name', 'user.last_name')

        When using SQLAlchemy models, you can reference related columns like this::
            class MyModelView(BaseModelView):
                column_list = ('<relationship>.<related column name>',)
    """

    column_details_list: Optional[List[str]] = None
    """
        Collection of the field names included in the details view.
        If set to `None`, will get them from the model.
    """

    column_export_list: Optional[List[str]] = None
    """
        Collection of the field names included in the export.
        If set to `None`, will get them from the model.
    """

    column_labels: Dict[str, str] = {}
    column_descriptions: Optional[Dict[str, str]] = None
    column_choices: Dict[str, Dict[Any, str]] = {}

    # cached list columns
    _list_columns: List[Tuple[str, str]] = []
    _details_columns: List[Tuple[str, str]] = []
    _export_columns: List[Tuple[str, str]] = []

    def scaffold_list_columns(self) -> List[str]:
        """Return the list of model field names to display in list views.

        Expected output is a list of column names, for example
        ``['name', 'first_name', 'last_name']``.

        Returns:
            List[str]: A list of field names.
        """
        return []

    def get_column_label(self, column_name: str) -> str:
        """Return a human-readable column label.

        If a label is defined in ``column_labels``, it is used; otherwise, the
        field name is converted into a display label.

        Args:
            column_name: Model field name.

        Returns:
            str: A formatted display label.
        """
        if self.column_labels and column_name in self.column_labels:
            return self.column_labels[column_name]
        else:
            return self._prettify_name(column_name)

    def _prettify_name(self, name: str) -> str:
        """Convert a field name into a readable display label.

        For example, ``user_name`` becomes ``User Name``.

        Args:
            name: Field name.

        Returns:
            str: Human-readable label.
        """
        return name.replace("_", " ").title()

    def get_column_names(self, columns: List[str]) -> List[Tuple[str, str]]:
        """Return column pairs of ``(field_name, label)`` for the given columns.

        Args:
            columns: List of columns to include.

        Returns:
            List[Tuple[str, str]]: A list of ``(field_name, label)`` tuples.
        """
        return [(c, self.get_column_label(c)) for c in columns]

    def get_list_columns(self) -> List[Tuple[str, str]]:
        """Return the columns displayed in the list view.

        If ``column_list`` is set, that list is used; otherwise, the method falls
        back to ``scaffold_list_columns()``.

        Returns:
            List[Tuple[str, str]]: ``(field_name, label)`` pairs for the list view.
        """
        return self.get_column_names(self.column_list or self.scaffold_list_columns())

    def get_details_columns(self) -> List[Tuple[str, str]]:
        """Return the columns displayed in the detail view.

        If ``column_details_list`` is set, that list is used; otherwise,
        ``scaffold_list_columns()`` is used as the fallback.

        Returns:
            List[Tuple[str, str]]: ``(field_name, label)`` pairs for the detail
                view.
        """
        return self.get_column_names(
            self.column_details_list or self.scaffold_list_columns()
        )

    def get_export_columns(self) -> List[Tuple[str, str]]:
        """Return the columns used in export output.

        The method prefers ``column_export_list``, then ``column_list``, and
        finally ``scaffold_list_columns()``.

        Returns:
            List[Tuple[str, str]]: ``(field_name, label)`` pairs for export.
        """
        return self.get_column_names(
            self.column_export_list or self.column_list or self.scaffold_list_columns()
        )

    def _get_column_by_idx(self, idx: Optional[int]) -> Optional[Tuple[str, str]]:
        """Return a column tuple by index.

        Args:
            idx: Column index in the list view.

        Returns:
            Optional[Tuple[str, str]]: A ``(field_name, label)`` tuple or
                ``None`` if the index is invalid.
        """
        if idx is None or idx < 0 or idx >= len(self._list_columns):
            return None

        return self._list_columns[idx]

    def search_placeholder(self) -> Optional[str]:
        """Build a search placeholder from the searchable column labels.

        Returns:
            Optional[str]: A label string such as ``"Name, Email"`` or ``None``
                when no searchable columns are configured.
        """
        if not self.column_searchable_list:
            return None

        placeholders = [
            self.column_labels.get(searchable, searchable)
            for searchable in self.column_searchable_list
        ]

        return ", ".join(placeholders)
