"""
排序管理 (Sorting Management)

负责管理 Admin 模型视图中的排序功能。
包括可排序列的脚手架生成、排序列的获取和排序状态管理。
"""

from typing import Optional, Dict, List, Tuple, Union


class SortingMixin:
    """
    排序管理功能混入类。

    提供排序列配置、排序状态管理等功能。
    """

    # 排序配置属性（继承自 ModelView）
    column_sortable_list: Optional[List[Union[str, Tuple[str, str]]]] = None
    column_default_sort: Optional[Union[str, Tuple[str, bool], List[Tuple[str, bool]]]] = None

    # 缓存的排序列
    _sortable_columns: Dict[str, Union[str, List[str]]] = {}

    def scaffold_sortable_columns(self) -> Dict[str, Union[str, List[str]]]:
        """
        Returns dictionary of sortable columns. Must be implemented in the child class.
        
        Expected return format is a dictionary, where keys are field names and values are property names.


        返回格式：字典，键是字段名，值是排序列名（例如属性名）。

        Returns:
            Dict[str, Union[str, List[str]]]: 可排序列的字典


        """
        return {}

    def get_sortable_columns(self) -> Dict[str, Union[str, List[str]]]:
        """
        Returns a dictionary of the sortable columns. Key is a model
        field name and value is sort column (for example - attribute).

        If `column_sortable_list` is set, will use it. Otherwise, will call
        `scaffold_sortable_columns` to get them from the model.
        
        获取可排序的列。

        如果设置了 column_sortable_list，使用它；
        否则调用 scaffold_sortable_columns() 从模型获取。

        Returns:
            Dict[str, Union[str, List[str]]]: 可排序列的字典
                键是模型字段名，值是排序列名（例如属性或列表）
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
        """
        Verify if column is sortable.

        Not case-sensitive.

        :param name:
            Column name.
            
        验证列是否可排序。

        不区分大小写。

        Args:
            name (str): 列名

        Returns:
            bool: 如果列可排序返回 True，否则返回 False
        """
        return name.lower() in (x.lower() for x in self._sortable_columns)

    def _get_default_order(self) -> Optional[List[Tuple[str, bool]]]:
        """
        Return default sort order.
        获取默认排序顺序。

        返回 (列名, 是否降序) 元组的列表。

        Returns:
            Optional[List[Tuple[str, bool]]]: 排序配置列表或 None
                例如 [('name', False), ('date', True)] 表示按 name 升序，date 降序
        """
        if self.column_default_sort:
            if isinstance(self.column_default_sort, list):
                # 已经是列表格式
                return self.column_default_sort
            elif isinstance(self.column_default_sort, tuple):
                # 单个元组，转换为列表
                return [self.column_default_sort]
            else:
                # 字符串格式，转换为 (column, False) 升序
                return [(self.column_default_sort, False)]

        return None
