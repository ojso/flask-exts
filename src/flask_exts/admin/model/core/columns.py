"""
列管理 (Column Management)

负责管理 Admin 模型视图中的列配置、标签和列表操作。
这包括列的脚手架生成、标签获取和各种视图的列列表管理。
"""

from typing import Optional, Tuple, List, Dict, Any


class ColumnsMixin:
    """
    列管理功能混入类。

    提供列脚手架、标签、列表等功能。
    """

    # 列配置属性（继承自 ModelView）
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

    # 缓存的列列表
    _list_columns: List[Tuple[str, str]] = []
    _details_columns: List[Tuple[str, str]] = []
    _export_columns: List[Tuple[str, str]] = []

    def scaffold_list_columns(self) -> List[str]:
        """
        Return list of the model field names. Must be implemented in the child class.
        
        Expected return format is list of strings of the field names. For example::
        
            ['name', 'first_name', 'last_name']

        Returns:
            List[str]: 字段名称列表

        Raises:
            NotImplementedError: 必须在子类中实现
        """
        raise NotImplementedError("Please implement scaffold_list_columns method")

    def get_column_label(self, column_name: str) -> str:
        """
        Return a human-readable column name.
        如果在 column_labels 中定义了标签，使用该标签；否则使用格式化的列名。
        
        :param column_name:
            Model field name.

        Returns:
            str: 格式化的列标签
        """
        if self.column_labels and column_name in self.column_labels:
            return self.column_labels[column_name]
        else:
            return self._prettify_name(column_name)

    def _prettify_name(self, name: str) -> str:
        """
        将字段名转换为友好的显示名。

        例如：user_name -> User name

        Args:
            name (str): 字段名

        Returns:
            str: 格式化后的名称
        """
        # 这个方法应该在父类中定义
        # 这里假设它存在或需要在子类中实现
        return name.replace('_', ' ').title()

    def get_column_names(self, columns: List[str]) -> List[Tuple[str, str]]:
        """
        Returns a list of tuples with the model field name and formatted field name.
        
        :param columns:
            List of columns to include in the results.


        Args:
            columns (List[str]): 列名列表

        Returns:
            List[Tuple[str, str]]: (字段名, 格式化名称) 的元组列表
        """
        return [(c, self.get_column_label(c)) for c in columns]

    def get_list_columns(self) -> List[Tuple[str, str]]:
        """
        Get a list of tuples with the model field name and formatted name for the columns in `column_list`.
        
        If `column_list` is not set, the columns from `scaffold_list_columns` will be used.

        获取列表视图中使用的列。

        如果设置了 column_list，使用它；否则使用 scaffold_list_columns() 返回的列。

        Returns:
            List[Tuple[str, str]]: (字段名, 标签) 的元组列表
        """
        return self.get_column_names(self.column_list or self.scaffold_list_columns())

    def get_details_columns(self) -> List[Tuple[str, str]]:
        """
        Get a list of tuples with the model field name and formatted name for the columns in `column_details_list`.
        If `column_details_list` is not set, the columns from `scaffold_list_columns` will be used.
        获取详情视图中使用的列。

        如果设置了 column_details_list，使用它；否则使用 scaffold_list_columns() 返回的列。

        Returns:
            List[Tuple[str, str]]: (字段名, 标签) 的元组列表
        """
        return self.get_column_names(
            self.column_details_list or self.scaffold_list_columns()
        )

    def get_export_columns(self) -> List[Tuple[str, str]]:
        """
        Get a list of tuples with the model field name and formatted name for the columns in `column_export_list`.
        If `column_export_list` is not set, it will attempt to use the columns from `column_list`
        or finally the columns from `scaffold_list_columns` will be used.
        获取导出视图中使用的列。

        首先尝试使用 column_export_list，然后 column_list，最后使用 scaffold_list_columns()。

        Returns:
            List[Tuple[str, str]]: (字段名, 标签) 的元组列表
        """
        return self.get_column_names(
            self.column_export_list or self.column_list or self.scaffold_list_columns()
        )

    def _get_column_by_idx(self, idx: Optional[int]) -> Optional[Tuple[str, str]]:
        """
        Return column index by idx.
        通过索引获取列。

        Args:
            idx (Optional[int]): 列索引

        Returns:
            Optional[Tuple[str, str]]: (字段名, 标签) 的元组，或 None 如果索引无效
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
        
        返回搜索占位符文本。

        基于 column_searchable_list 和 column_labels 生成。

        例如，如果 column_searchable_list = ('name', 'email')
        则返回 "Name, Email"

        Returns:
            Optional[str]: 搜索占位符或 None
        """
        if not self.column_searchable_list:
            return None

        placeholders = [
            self.column_labels.get(searchable, searchable)
            for searchable in self.column_searchable_list
        ]

        return ", ".join(placeholders)
