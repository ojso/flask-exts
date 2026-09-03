"""
English: Pagination builder / 分页构建器

English: Used to build pagination conditions. / 用于构建分页条件。
"""


class PaginationBuilder:
    """English: Build pagination conditions / 构建分页条件"""

    def __init__(self):
        self.page = None
        self.page_size = None

    def set_page(self, page, page_size):
        """English: Set pagination / 设置分页

        Args:
            page: page number starting from 1 / 页码（从 1 开始）
            page_size: number of rows per page / 每页大小
        """
        self.page = page
        self.page_size = page_size
        return self

    def build(self, query):
        """English: Apply pagination to the query / 应用分页到查询

        Args:
            query: SQLAlchemy query object / SQLAlchemy 查询对象

        Returns:
            Query with pagination applied / 应用分页后的查询
        """
        if self.page and self.page_size:
            offset = (self.page - 1) * self.page_size
            query = query.offset(offset).limit(self.page_size)

        return query

    def reset(self):
        """English: Reset pagination conditions / 重置分页条件"""
        self.page = None
        self.page_size = None
        return self
