"""Relationship handler for SQLAlchemy models."""

from sqlalchemy import inspect


class RelationshipsHandler:
    """Resolve relationship metadata and apply eager joins."""

    def __init__(self, view):
        self.view = view

    def get_related_models(self, model):
        """Return the related model classes for a mapped model."""
        mapper = inspect(model)
        relations = {}

        for prop in mapper.relationships:
            relations[prop.key] = prop.mapper.class_

        return relations

    def init_auto_joins(self):
        """Initialize the configured automatic relationship joins."""
        self.auto_joins = []

        if hasattr(self.view, "column_auto_select_related"):
            for column in self.view.column_auto_select_related:
                self.auto_joins.append(column)

    def apply_auto_joins(self, query):
        """Apply any configured automatic joins to the SQLAlchemy query."""
        if hasattr(self, "auto_joins"):
            for join_spec in self.auto_joins:
                if isinstance(join_spec, str):
                    related_model = getattr(self.view.model, join_spec, None)
                    if related_model is not None:
                        query = query.joinedload(related_model)
                else:
                    query = query.joinedload(join_spec)

        return query
