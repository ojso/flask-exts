"""
Filter builder / 过滤器构建器

Used to build complex filter conditions. / 用于构建复杂的过滤条件。
"""


class FilterBuilder:
    """English: Build filter conditions / 构建过滤条件"""

    def __init__(self):
        self.filters = []

    def add_filter(self, column, operator, value):
        """English: Add a filter condition / 添加过滤条件

        Args:
            column: SQLAlchemy column / SQLAlchemy 列
            operator: comparison operator / 操作符（'=', '!=', '>', '<', 'like', 'in'）
            value: filter value / 过滤值
        """
        self.filters.append((column, operator, value))
        return self

    def build(self, query):
        """English: Apply all filter conditions to the query / 应用所有过滤条件到查询

        Args:
            query: SQLAlchemy query object / SQLAlchemy 查询对象

        Returns:
            Query with filters applied / 应用过滤后的查询
        """
        for column, operator, value in self.filters:
            if operator == '=':
                query = query.filter(column == value)
            elif operator == '!=':
                query = query.filter(column != value)
            elif operator == '>':
                query = query.filter(column > value)
            elif operator == '<':
                query = query.filter(column < value)
            elif operator == 'like':
                query = query.filter(column.like(value))
            elif operator == 'in':
                query = query.filter(column.in_(value))

        return query

    def reset(self):
        """English: Reset filter conditions / 重置过滤条件"""
        self.filters = []
        return self
