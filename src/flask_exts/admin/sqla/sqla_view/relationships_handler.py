"""
关系处理器

处理 SQLAlchemy 关系的连接和加载。
"""

from sqlalchemy import inspect


class RelationshipsHandler:
    """English: handle SQLAlchemy / 处理 SQLAlchemy 关系的连接和加载"""

    def __init__(self, view):
        self.view = view

    def get_related_models(self, model):
        """English: comment / 获取模型的相关关系"""
        mapper = inspect(model)
        relations = {}
        
        for prop in mapper.relationships:
            relations[prop.key] = prop.mapper.class_
        
        return relations

    def init_auto_joins(self):
        """English: comment / 初始化自动连接关系"""
        self.auto_joins = []
        
        if hasattr(self.view, "column_auto_select_related"):
            for column in self.view.column_auto_select_related:
                self.auto_joins.append(column)

    def apply_auto_joins(self, query):
        """English: comment / 应用自动连接关系"""
        if hasattr(self, "auto_joins"):
            for join_spec in self.auto_joins:
                if isinstance(join_spec, str):
                    # English: comment / 字符串形式的关系名称
                    related_model = getattr(self.view.model, join_spec, None)
                    if related_model is not None:
                        query = query.joinedload(related_model)
                else:
                    # English: comment / 直接的关系对象
                    query = query.joinedload(join_spec)
        
        return query
