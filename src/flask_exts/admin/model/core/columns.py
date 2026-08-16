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
    column_details_list: Optional[List[str]] = None
    column_export_list: Optional[List[str]] = None
    column_labels: Dict[str, str] = {}
    column_descriptions: Optional[Dict[str, str]] = None
    column_choices: Dict[str, Dict[Any, str]] = {}

    # 缓存的列列表
    _list_columns: List[Tuple[str, str]] = []
    _details_columns: List[Tuple[str, str]] = []
    _export_columns: List[Tuple[str, str]] = []

    def scaffold_list_columns(self) -> List[str]:
        """
        返回模型字段名称列表。必须在子类中实现。

        返回格式：字段名称列表，例如 ['name', 'first_name', 'last_name']

        Returns:
            List[str]: 字段名称列表

        Raises:
            NotImplementedError: 必须在子类中实现
        """
        raise NotImplementedError("Please implement scaffold_list_columns method")

    def get_column_label(self, column_name: str) -> str:
        """
        返回可读的列名。

        如果在 column_labels 中定义了标签，使用该标签；
        否则使用格式化的列名。

        Args:
            column_name (str): 模型字段名

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
        返回模型字段名和格式化字段名的元组列表。

        Args:
            columns (List[str]): 列名列表

        Returns:
            List[Tuple[str, str]]: (字段名, 格式化名称) 的元组列表
        """
        return [(c, self.get_column_label(c)) for c in columns]

    def get_list_columns(self) -> List[Tuple[str, str]]:
        """
        获取列表视图中使用的列。

        如果设置了 column_list，使用它；否则使用 scaffold_list_columns() 返回的列。

        Returns:
            List[Tuple[str, str]]: (字段名, 标签) 的元组列表
        """
        return self.get_column_names(self.column_list or self.scaffold_list_columns())

    def get_details_columns(self) -> List[Tuple[str, str]]:
        """
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
