"""
Pagination management / 分页管理

English summary: This module handles pagination state for Admin model views, including extracting query parameters, validating page sizes, and building page URLs.
中文说明：这个模块负责管理 Admin 模型视图中的分页状态，包括提取查询参数、校验页大小和生成分页 URL。
"""

from typing import Optional, Tuple, Dict, Any
from flask import request


class ViewArgs:
    """List view arguments."""
    def __init__(self, page=0, page_size=0, sort=None, sort_desc=False, search=None, filters=None, extra_args=None):
        self.page = page
        self.page_size = page_size
        self.sort = sort
        self.sort_desc = sort_desc
        self.search = search
        self.filters = filters or []
        self.extra_args = extra_args or {}

    def clone(self, **kwargs):
        """English: comment / 克隆视图参数，覆盖指定的参数"""
        args = {
            'page': self.page,
            'page_size': self.page_size,
            'sort': self.sort,
            'sort_desc': self.sort_desc,
            'search': self.search,
            'filters': self.filters,
            'extra_args': self.extra_args.copy()
        }
        args.update(kwargs)
        return ViewArgs(**args)


class PaginationMixin:
    """
    Pagination mixin / 分页管理功能混入类

    English summary: Provides pagination parameter extraction, validation, and URL generation for list views.
    中文说明：提供列表视图的分页参数提取、校验和 URL 生成功能。
    """

    # Pagination settings
    page_size: int = 20
    """
        Default page size for pagination.
    """

    can_set_page_size = True
    """
        Allows to select page size via dropdown list
    """

    page_size_options: tuple = (5, 10, 20, 50, 100)
    """
        Sets the page size options available, if `can_set_page_size` is True
    """


    def get_safe_page_size(self, page_size: int) -> int:
        """
        获取安全的页大小。

        如果 can_set_page_size 为 True 且 page_size 在 page_size_options 中，
        则使用提供的 page_size；否则使用默认的 page_size。

        Args:
            page_size (int): 请求的页大小

        Returns:
            int: 安全的页大小
        """
        if self.can_set_page_size and page_size in self.page_size_options:
            return page_size
        return self.page_size

    def _get_list_args(self) -> 'ViewArgs':
        """
        Return arguments from query.

        提取分页、排序、搜索和过滤参数。

        Returns:
            ViewArgs: 包含所有视图参数的对象
        """
        # English: note get_active_filters method / 注意：这里假设存在 get_active_filters() 方法
        # English: FilterMixin / 该方法应在 FilterMixin 中定义
        return ViewArgs(
            page=request.args.get("page", 0, type=int),
            page_size=request.args.get("page_size", 0, type=int),
            sort=request.args.get("sort", None, type=int),
            sort_desc=request.args.get("desc", None, type=int),
            search=request.args.get("search", None),
            filters=self.get_active_filters() if hasattr(self, 'get_active_filters') else [],
            extra_args=dict(
                [
                    (k, v)
                    for k, v in request.args.items()
                    if k
                    not in (
                        "page",
                        "page_size",
                        "sort",
                        "desc",
                        "search",
                    )
                    and not k.startswith("flt")
                ]
            ),
        )

    def _get_list_url(self, view_args: 'ViewArgs') -> str:
        """
        Generate page URL with current page, sort column and other parameters.

        :param view:
            View name
        :param view_args:
            ViewArgs object with page number, filters, etc.

        生成带有当前页、排序列和其他参数的页面 URL。

        Args:
            view_args (ViewArgs): 视图参数对象

        Returns:
            str: 生成的 URL
        """
        page = view_args.page or None
        desc = 1 if view_args.sort_desc else None

        kwargs = dict(
            page=page, sort=view_args.sort, desc=desc, search=view_args.search
        )
        kwargs.update(view_args.extra_args)

        kwargs["page_size"] = self.get_safe_page_size(view_args.page_size)

        # English: note get_active_filters_kwargs get_url method / 注意：这里假设存在 get_active_filters_kwargs() 和 get_url() 方法
        if hasattr(self, 'get_active_filters_kwargs'):
            kwargs.update(self.get_active_filters_kwargs(view_args.filters))

        if hasattr(self, 'get_url'):
            return self.get_url(".index_view", **kwargs)
        else:
            # English: get_url / 返回基本格式，子类应实现 get_url()
            return f"?{'&'.join(f'{k}={v}' for k, v in kwargs.items() if v)}"
