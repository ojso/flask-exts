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
        """
        Return list of the model field names.

        Expected return format is list of strings of the field names. For example::

            ['name', 'first_name', 'last_name']

        Returns:
            List[str]: Field name list / 字段名称列表
        """
        return []

    def get_column_label(self, column_name: str) -> str:
        """
        Return a human-readable column name.
        English summary: If a label is defined in column_labels, use it; otherwise format the field name into a display label.
        中文说明：如果在 column_labels 中定义了标签，使用该标签；否则使用格式化的列名。

        :param column_name:
            Model field name.

        Returns:
            str: Formatted column label / 格式化的列标签
        """
        if self.column_labels and column_name in self.column_labels:
            return self.column_labels[column_name]
        else:
            return self._prettify_name(column_name)

    def _prettify_name(self, name: str) -> str:
        """
        English summary: Convert a field name into a friendlier display name such as user_name -> User name.
        中文说明：将字段名转换为友好的显示名，例如：user_name -> User name。

        Args:
            name (str): Field name / 字段名

        Returns:
            str: Formatted name / 格式化后的名称
        """
        # English: comment / This method should be defined in the parent class.
        # English: comment / Here we assume it exists or should be implemented in a subclass.
        return name.replace("_", " ").title()

    def get_column_names(self, columns: List[str]) -> List[Tuple[str, str]]:
        """
        Returns a list of tuples with the model field name and formatted field name.

        :param columns:
            List of columns to include in the results.

        Args:
            columns (List[str]): Column names / 列名列表

        Returns:
            List[Tuple[str, str]]: (field name, formatted name) tuples / (字段名, 格式化名称) 的元组列表
        """
        return [(c, self.get_column_label(c)) for c in columns]

    def get_list_columns(self) -> List[Tuple[str, str]]:
        """
        Get a list of tuples with the model field name and formatted name for the columns in `column_list`.

        If `column_list` is not set, the columns from `scaffold_list_columns` will be used.

        English summary: Return the columns used by the list view.
        中文说明：获取列表视图中使用的列。如果设置了 column_list，使用它；否则使用 scaffold_list_columns() 返回的列。

        Returns:
            List[Tuple[str, str]]: (field name, label) tuples / (字段名, 标签) 的元组列表
        """
        return self.get_column_names(self.column_list or self.scaffold_list_columns())

    def get_details_columns(self) -> List[Tuple[str, str]]:
        """
        Get a list of tuples with the model field name and formatted name for the columns in `column_details_list`.
        If `column_details_list` is not set, the columns from `scaffold_list_columns` will be used.

        English summary: Return the columns shown in the detail view.
        中文说明：获取详情视图中使用的列。如果设置了 column_details_list，使用它；否则使用 scaffold_list_columns() 返回的列。

        Returns:
            List[Tuple[str, str]]: (field name, label) tuples / (字段名, 标签) 的元组列表
        """
        return self.get_column_names(
            self.column_details_list or self.scaffold_list_columns()
        )

    def get_export_columns(self) -> List[Tuple[str, str]]:
        """
        Get a list of tuples with the model field name and formatted name for the columns in `column_export_list`.
        If `column_export_list` is not set, it will attempt to use the columns from `column_list`
        or finally the columns from `scaffold_list_columns` will be used.

        English summary: Return the columns used by the export view.
        中文说明：获取导出视图中使用的列。首先尝试使用 column_export_list，然后 column_list，最后使用 scaffold_list_columns()。

        Returns:
            List[Tuple[str, str]]: (field name, label) tuples / (字段名, 标签) 的元组列表
        """
        return self.get_column_names(
            self.column_export_list or self.column_list or self.scaffold_list_columns()
        )

    def _get_column_by_idx(self, idx: Optional[int]) -> Optional[Tuple[str, str]]:
        """
        Return column index by idx.

        English summary: Look up a column tuple by index in the list view columns.
        中文说明：通过索引获取列。

        Args:
            idx (Optional[int]): Column index / 列索引

        Returns:
            Optional[Tuple[str, str]]: (field name, label) tuple or None when the index is invalid / (字段名, 标签) 的元组，或 None 如果索引无效
        """
        if idx is None or idx < 0 or idx >= len(self._list_columns):
            return None

        return self._list_columns[idx]

    def search_placeholder(self) -> Optional[str]:
        """
        Return search placeholder.

        For example, if set column_labels and column_searchable_list:

        class MyModelView(BaseModelView):
            column_labels = dict(name='Name', last_name='Last Name')
            column_searchable_list = ('name', 'last_name')

        placeholder is: "Name, Last Name"

        English summary: Build a search placeholder text from the searchable column labels.
        中文说明：返回搜索占位符文本。基于 column_searchable_list 和 column_labels 生成，例如，如果 column_searchable_list = ('name', 'email')，则返回 "Name, Email"。

        Returns:
            Optional[str]: Search placeholder or None / 搜索占位符或 None
        """
        if not self.column_searchable_list:
            return None

        placeholders = [
            self.column_labels.get(searchable, searchable)
            for searchable in self.column_searchable_list
        ]

        return ", ".join(placeholders)
