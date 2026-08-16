"""
读取操作 (Read Operations)

负责从数据源读取模型数据的操作。
"""

from typing import Tuple, List, Any, Optional


class ReadOperationsMixin:
    """
    读取操作功能混入类。

    提供 get_list 和 get_one 方法。
    """

    def get_list(
        self,
        page: int,
        sort_field: Optional[str],
        sort_desc: bool,
        search: Optional[str],
        filters: List[Tuple],
        page_size: Optional[int] = None,
    ) -> Tuple[Optional[int], List[Any]]:
        """
        从数据源返回分页和排序的模型列表。

        必须在子类中实现。

        Args:
            page (int): 页号（0 为第一页）
            sort_field (Optional[str]): 排序列名或 None
            sort_desc (bool): 如果为 True，按降序排序
            search (Optional[str]): 搜索查询
            filters (List[Tuple]): 过滤器元组列表。
                第一个值是搜索索引，第二个值是搜索值。
            page_size (Optional[int]): 结果数。默认为 ModelView 的 page_size。
                可以重写以改变 page_size 限制。
                删除 page_size 限制需要将 page_size 设置为 0 或 False。

        Returns:
            Tuple[Optional[int], List[Any]]: (总记录数, 模型列表)
                总记录数可以为 None 如果无法计算

        Raises:
            NotImplementedError: 必须在子类中实现
        """
        raise NotImplementedError("Please implement get_list method")

    def get_one(self, id: Any) -> Optional[Any]:
        """
        通过 id 返回一个模型。

        必须在子类中实现。

        Args:
            id (Any): 模型 id

        Returns:
            Optional[Any]: 模型实例或 None

        Raises:
            NotImplementedError: 必须在子类中实现
        """
        raise NotImplementedError("Please implement get_one method")

    def get_pk_value(self, obj: Any) -> Any:
        """
        从模型对象返回主键值。

        必须在子类中实现。

        Args:
            obj (Any): 模型对象

        Returns:
            Any: 主键值

        Raises:
            NotImplementedError: 必须在子类中实现
        """
        raise NotImplementedError("Please implement get_pk_value method")
