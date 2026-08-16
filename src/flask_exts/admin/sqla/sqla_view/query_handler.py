"""
查询处理器

处理 SQLAlchemy 查询的构建和过滤逻辑。
"""


class QueryHandler:
    """处理 SQLAlchemy 查询的构建和过滤"""

    def __init__(self, view):
        self.view = view

    def apply_search(self, query, search):
        """应用搜索过滤"""
        if search:
            search_query = None
            values = search.split(" ")

            for column in self.view.column_searchable_list:
                for value in values:
                    query = query.filter(column.ilike("%" + value + "%"))

        return query

    def apply_filters(self, query, filters):
        """应用筛选条件"""
        if filters:
            for filter_name, filter_value in filters.items():
                col_filter = self.view._filters.get(filter_name)
                if col_filter:
                    query = col_filter.apply(query, filter_value)

        return query
