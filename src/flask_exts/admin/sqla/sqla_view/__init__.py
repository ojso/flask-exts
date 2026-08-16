"""
SQLAlchemy 视图处理模块

将 view.py 中的各个处理逻辑分离为独立的处理器模块，提高代码的可维护性和可测试性。

模块结构：
- QueryHandler: 处理查询的构建和过滤
- SortingHandler: 处理排序逻辑
- PaginationHandler: 处理分页逻辑
- RelationshipsHandler: 处理关系连接和加载
"""

from .query_handler import QueryHandler
from .sorting_handler import SortingHandler
from .pagination_handler import PaginationHandler
from .relationships_handler import RelationshipsHandler

__all__ = [
    'QueryHandler',
    'SortingHandler',
    'PaginationHandler',
    'RelationshipsHandler',
]
