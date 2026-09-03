"""
SQLAlchemy view processing module / SQLAlchemy 视图处理模块

English summary: This package separates the view-processing logic from ModelView into dedicated handler modules to improve maintainability and testability.
中文说明：将 view.py 中的各个处理逻辑分离为独立的处理器模块，提高代码的可维护性和可测试性。

Module structure:
- QueryHandler: handles query building and filters / 处理查询的构建和过滤
- SortingHandler: handles sorting logic / 处理排序逻辑
- PaginationHandler: handles pagination logic / 处理分页逻辑
- RelationshipsHandler: handles relationship joins and loading / 处理关系连接和加载
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
