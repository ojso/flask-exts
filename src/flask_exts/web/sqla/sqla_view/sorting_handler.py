"""Sorting handler for SQLAlchemy-backed model views."""


class SortingHandler:
    """Apply sorting logic to a SQLAlchemy query."""

    def __init__(self, view):
        self.view = view

    def apply_sorting(self, query, sort_column, sort_desc):
        """Apply sorting to the query when a sortable column is selected."""
        if sort_column:
            if sort_column in self.view.column_sortable_list:
                column = self.view.model_admin.get_column_for_field_name(
                    self.view.model, sort_column
                )
                if column is not None:
                    if sort_desc:
                        query = query.order_by(column.desc())
                    else:
                        query = query.order_by(column)

        return query
