"""
分页处理器

处理查询结果的分页逻辑。
"""


class PaginationHandler:
    """处理分页逻辑"""

    def __init__(self, view):
        self.view = view

    def apply_pagination(self, query, page, page_size):
        """应用分页"""
        if page and page_size:
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

        return query

    def get_page_count(self, total_count, page_size):
        """获取总页数"""
        if page_size == 0:
            return 1
        return (total_count + page_size - 1) // page_size
