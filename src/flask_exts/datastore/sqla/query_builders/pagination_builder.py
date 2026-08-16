"""
分页构建器

用于构建分页条件。
"""


class PaginationBuilder:
    """构建分页条件"""

    def __init__(self):
        self.page = None
        self.page_size = None

    def set_page(self, page, page_size):
        """设置分页
        
        Args:
            page: 页码（从 1 开始）
            page_size: 每页大小
        """
        self.page = page
        self.page_size = page_size
        return self

    def build(self, query):
        """应用分页到查询
        
        Args:
            query: SQLAlchemy 查询对象
            
        Returns:
            应用分页后的查询
        """
        if self.page and self.page_size:
            offset = (self.page - 1) * self.page_size
            query = query.offset(offset).limit(self.page_size)
        
        return query

    def reset(self):
        """重置分页条件"""
        self.page = None
        self.page_size = None
        return self
