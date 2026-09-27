"""Builder for composing SQLAlchemy pagination clauses."""


class PaginationBuilder:
    """Build and apply pagination to a query."""

    def __init__(self):
        self.page = None
        self.page_size = None

    def set_page(self, page, page_size):
        """Set the page number and page size.

        Args:
            page: Page number starting from 1.
            page_size: Number of rows per page.
        """
        self.page = page
        self.page_size = page_size
        return self

    def build(self, query):
        """Apply pagination to the query.

        Args:
            query: SQLAlchemy query object.

        Returns:
            Query with pagination applied.
        """
        if self.page and self.page_size:
            offset = (self.page - 1) * self.page_size
            query = query.offset(offset).limit(self.page_size)

        return query

    def reset(self):
        """Clear the configured pagination state."""
        self.page = None
        self.page_size = None
        return self
