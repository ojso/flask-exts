from typing import Tuple, List, Any, Optional


class ReadOperationsMixin:
    """
    Read operations mixin / 读取操作功能混入类

    English summary: Provides data access methods for reading model records, including list retrieval and single-record lookup.
    中文说明：提供读取模型数据的方法，包括列表检索和单条记录查询。
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
        Return a tuple of a count of results and a paginated and sorted list of models from the data source.

        Must be implemented in the child class.

        :param page:
            Page number, 0 based. Can be set to None if it is first page.
        :param sort_field:
            Sort column name or None.
        :param sort_desc:
            If set to True, sorting is in descending order.
        :param search:
            Search query
        :param filters:
            List of filter tuples. First value in a tuple is a search
            index, second value is a search value.
        :param page_size:
            Number of results. Defaults to ModelView's page_size. Can be
            overriden to change the page_size limit. Removing the page_size
            limit requires setting page_size to 0 or False.
            
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
        Return one model by its id.

        Must be implemented in the child class.

        :param id:
            Model id

        Return one model by its id.

        Args:
            id (Any): Model id

        Returns:
            Optional[Any]: model instance or None

        Raises:
            NotImplementedError: must be implemented in subclass
        """
        raise NotImplementedError("Please implement get_one method")

    def get_pk_value(self, obj: Any) -> Any:
        """
        Return PK value from a model object.
        """
        raise NotImplementedError("Please implement get_pk_value method")
