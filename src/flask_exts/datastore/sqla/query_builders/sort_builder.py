"""
排序构建器

用于构建排序条件。
"""


class SortBuilder:
    """构建排序条件"""

    def __init__(self):
        self.sorts = []

    def add_sort(self, column, desc=False):
        """添加排序条件
        
        Args:
            column: SQLAlchemy 列
            desc: 是否降序
        """
        self.sorts.append((column, desc))
        return self

    def build(self, query):
        """应用所有排序条件到查询
        
        Args:
            query: SQLAlchemy 查询对象
            
        Returns:
            应用排序后的查询
        """
        for column, desc in self.sorts:
            if desc:
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column)
        
        return query

    def reset(self):
        """重置排序条件"""
        self.sorts = []
        return self
