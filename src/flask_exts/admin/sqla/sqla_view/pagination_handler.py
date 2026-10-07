"""Pagination handler for SQLAlchemy-backed admin queries."""


class PaginationHandler:
    """Apply pagination to a SQLAlchemy query."""

    def __init__(self, view):
        self.view = view

    def apply_pagination(self, query, page, page_size):
        """Apply offset and limit to the query."""
        if page and page_size:
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

        return query

    def get_page_count(self, total_count, page_size):
        """Return the total page count for the given result size."""
        if page_size == 0:
            return 1
        return (total_count + page_size - 1) // page_size
