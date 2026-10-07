"""Query handler for SQLAlchemy-backed view logic."""


class QueryHandler:
    """Apply search and filter logic to SQLAlchemy queries."""

    def __init__(self, view):
        self.view = view

    def apply_search(self, query, search):
        """Apply search conditions to the query."""
        if search:
            values = search.split(" ")

            for column in self.view.column_searchable_list:
                for value in values:
                    query = query.filter(column.ilike("%" + value + "%"))

        return query

    def apply_filters(self, query, filters):
        """Apply filter values to the query."""
        if filters:
            for filter_name, filter_value in filters.items():
                col_filter = self.view._filters.get(filter_name)
                if col_filter:
                    query = col_filter.apply(query, filter_value)

        return query
