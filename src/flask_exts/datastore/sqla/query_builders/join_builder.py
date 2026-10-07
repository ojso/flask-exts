"""Builder for composing SQLAlchemy join clauses."""


class JoinBuilder:
    """Build and apply JOIN conditions to a query."""

    def __init__(self):
        self.joins = []

    def add_join(self, target, onclause=None, isouter=False):
        """Add a JOIN condition.

        Args:
            target: Target table or model to join.
            onclause: JOIN condition.
            isouter: Whether to use an outer join.
        """
        self.joins.append((target, onclause, isouter))
        return self

    def add_joinedload(self, relationship):
        """Add a joinedload instruction for relationship eager loading.

        Args:
            relationship: SQLAlchemy relationship object.
        """
        self.joins.append(('joinedload', relationship, None))
        return self

    def build(self, query):
        """Apply all JOIN conditions to the query.

        Args:
            query: SQLAlchemy query object.

        Returns:
            Query with joins applied.
        """
        for item in self.joins:
            if item[0] == 'joinedload':
                query = query.joinedload(item[1])
            else:
                target, onclause, isouter = item
                query = query.join(target, onclause, isouter=isouter)

        return query

    def reset(self):
        """Clear all configured joins."""
        self.joins = []
        return self
