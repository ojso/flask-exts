"""Builder for composing SQLAlchemy filter clauses."""


class FilterBuilder:
    """Build and apply filter conditions to a query."""

    def __init__(self):
        self.filters = []

    def add_filter(self, column, operator, value):
        """Add a filter condition.

        Args:
            column: SQLAlchemy column to filter on.
            operator: Comparison operator such as ``=``, ``!=``, ``>``,
                ``<``, ``like``, or ``in``.
            value: Filter value.
        """
        self.filters.append((column, operator, value))
        return self

    def build(self, query):
        """Apply all filter conditions to the query.

        Args:
            query: SQLAlchemy query object.

        Returns:
            Query with filters applied.
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
        """Clear all configured filter conditions."""
        self.filters = []
        return self
