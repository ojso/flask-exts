"""Builder for composing SQLAlchemy sort clauses."""


class SortBuilder:
    """Build and apply ordering conditions to a query."""

    def __init__(self):
        self.sorts = []

    def add_sort(self, column, desc=False):
        """Add a sort condition.

        Args:
            column: SQLAlchemy column to sort by.
            desc: Whether to sort in descending order.
        """
        self.sorts.append((column, desc))
        return self

    def build(self, query):
        """Apply all sort conditions to the query.

        Args:
            query: SQLAlchemy query object.

        Returns:
            Query with sorting applied.
        """
        for column, desc in self.sorts:
            if desc:
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column)

        return query

    def reset(self):
        """Clear all configured sort conditions."""
        self.sorts = []
        return self
