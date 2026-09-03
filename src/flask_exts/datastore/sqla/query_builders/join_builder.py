"""
English: Join builder / 连接构建器

English: Used to build SQLAlchemy JOIN conditions. / 用于构建 SQLAlchemy JOIN 条件。
"""


class JoinBuilder:
    """English: Build JOIN conditions / 构建 JOIN 条件"""

    def __init__(self):
        self.joins = []

    def add_join(self, target, onclause=None, isouter=False):
        """English: Add a JOIN condition / 添加 JOIN 条件

        Args:
            target: target table/model to join / 要连接的目标表/模型
            onclause: JOIN condition / JOIN 条件
            isouter: whether to use an outer join / 是否外连接
        """
        self.joins.append((target, onclause, isouter))
        return self

    def add_joinedload(self, relationship):
        """English: Add joinedload / 添加 joinedload（用于优化加载关系）

        Args:
            relationship: relationship object / 关系对象
        """
        self.joins.append(('joinedload', relationship, None))
        return self

    def build(self, query):
        """English: Apply all JOIN conditions to the query / 应用所有 JOIN 条件到查询

        Args:
            query: SQLAlchemy query object / SQLAlchemy 查询对象

        Returns:
            Query with JOINs applied / 应用 JOIN 后的查询
        """
        for item in self.joins:
            if item[0] == 'joinedload':
                query = query.joinedload(item[1])
            else:
                target, onclause, isouter = item
                query = query.join(target, onclause, isouter=isouter)

        return query

    def reset(self):
        """English: Reset JOIN conditions / 重置 JOIN 条件"""
        self.joins = []
        return self
