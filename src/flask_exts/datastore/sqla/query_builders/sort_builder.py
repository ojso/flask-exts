"""
English: Sort builder / 排序构建器

English: Used to build sorting conditions. / 用于构建排序条件。
"""


class SortBuilder:
    """English: Build sorting conditions / 构建排序条件"""

    def __init__(self):
        self.sorts = []

    def add_sort(self, column, desc=False):
        """English: Add a sort condition / 添加排序条件

        Args:
            column: SQLAlchemy column / SQLAlchemy 列
            desc: whether to sort in descending order / 是否降序
        """
        self.sorts.append((column, desc))
        return self

    def build(self, query):
        """English: Apply all sort conditions to the query / 应用所有排序条件到查询

        Args:
            query: SQLAlchemy query object / SQLAlchemy 查询对象

        Returns:
            Query with sorting applied / 应用排序后的查询
        """
        for column, desc in self.sorts:
            if desc:
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column)

        return query

    def reset(self):
        """English: Reset sort conditions / 重置排序条件"""
        self.sorts = []
        return self
