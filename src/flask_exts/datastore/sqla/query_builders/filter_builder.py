"""
过滤器构建器

用于构建复杂的过滤条件。
"""


class FilterBuilder:
    """构建过滤条件"""

    def __init__(self):
        self.filters = []

    def add_filter(self, column, operator, value):
        """添加过滤条件
        
        Args:
            column: SQLAlchemy 列
            operator: 操作符（'=', '!=', '>', '<', 'like', 'in'）
            value: 过滤值
        """
        self.filters.append((column, operator, value))
        return self

    def build(self, query):
        """应用所有过滤条件到查询
        
        Args:
            query: SQLAlchemy 查询对象
            
        Returns:
            应用过滤后的查询
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
        """重置过滤条件"""
        self.filters = []
        return self
