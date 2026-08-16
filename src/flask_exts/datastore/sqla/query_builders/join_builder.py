"""
连接构建器

用于构建 SQLAlchemy JOIN 条件。
"""


class JoinBuilder:
    """构建 JOIN 条件"""

    def __init__(self):
        self.joins = []

    def add_join(self, target, onclause=None, isouter=False):
        """添加 JOIN 条件
        
        Args:
            target: 要连接的目标表/模型
            onclause: JOIN 条件
            isouter: 是否外连接
        """
        self.joins.append((target, onclause, isouter))
        return self

    def add_joinedload(self, relationship):
        """添加 joinedload（用于优化加载关系）
        
        Args:
            relationship: 关系对象
        """
        self.joins.append(('joinedload', relationship, None))
        return self

    def build(self, query):
        """应用所有 JOIN 条件到查询
        
        Args:
            query: SQLAlchemy 查询对象
            
        Returns:
            应用 JOIN 后的查询
        """
        for item in self.joins:
            if item[0] == 'joinedload':
                query = query.joinedload(item[1])
            else:
                target, onclause, isouter = item
                query = query.join(target, onclause, isouter=isouter)
        
        return query

    def reset(self):
        """重置 JOIN 条件"""
        self.joins = []
        return self
