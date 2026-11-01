"""Mock ModelView for testing purposes."""

from flask_exts.admin.model.view import ModelView


class MockModelView(ModelView):
    """Mock ModelView for testing.

    This class provides a minimal implementation of ModelView methods
    needed for testing CRUD operations without requiring a full Flask app.
    """

    def __init__(self, model=None, backend_factory=None, **kwargs):
        """Initialize the mock view.

        Args:
            model: The model class to use.
            backend_factory: Factory to create backend instances.
            **kwargs: Additional keyword arguments
                - column_list
                - column_labels
                - column_sortable_list
                - can_create
                - can_edit
                - can_delete
                - can_export
                - etc
        """
        # Extract configuration parameters from kwargs before passing to parent
        self.column_list = kwargs.pop("column_list", None)
        self.column_labels = kwargs.pop("column_labels", None)
        self.column_sortable_list = kwargs.pop("column_sortable_list", None)
        self.column_details_list = kwargs.pop("column_details_list", None)
        self.form_columns = kwargs.pop("form_columns", None)
        self.column_formatters = kwargs.pop("column_formatters", None)
        self.column_formatters_detail = kwargs.pop("column_formatters_detail", None)

        # Permission flags
        self.can_create = kwargs.pop("can_create", True)
        self.can_edit = kwargs.pop("can_edit", True)
        self.can_delete = kwargs.pop("can_delete", True)
        self.can_export = kwargs.pop("can_export", False)

        # Pass remaining kwargs to parent
        super().__init__(model=model, backend_factory=backend_factory, **kwargs)

    def get_data(self):
        """Return the data in the backend."""
        return self._backend.get_data()
