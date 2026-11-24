from sqlalchemy import inspect


class InlineForm:
    """Settings for inline model form.

    You can use this class to customize displayed form.

    For example::

        class MyUserInlineForm(InlineForm):
            form_columns = ('name', 'email')
    """

    form_columns = None
    form_excluded_columns = None
    form_args = None
    form_extra_fields = None
    column_labels = None
    column_descriptions = None

    def __init__(self, model, **kwargs):
        """Initialize inline form settings for a model.

        Args:
            model: Model class.
            kwargs: Additional options.
        """
        self.model = model
        self._ajax_refs = {}

        for k, v in kwargs.items():
            setattr(self, k, v)

        if self.form_columns is None:
            self.form_columns = self._get_default_form_columns()

    def get_ajax_loader(self, name):
        """Return the AJAX loader registered for a child relationship field.

        Args:
            name: Relationship attribute name on the child model.

        Returns:
            AjaxModelLoader | None: Loader resolved from ``ajax_refs``.
        """
        return self._ajax_refs.get(name)

    def get_column_label(self, column_name, default_label=None):
        """Return a human-readable label for a generated child form field.

        Args:
            column_name: Model field name.
            default_label: Explicit label that takes precedence.

        Returns:
            str: Display label.
        """
        if self.column_labels and column_name in self.column_labels:
            return self.column_labels[column_name]

        if default_label:
            return default_label

        return column_name.replace("_", " ").title()

    def get_column_description(self, column_name):
        """Return a description for a generated child form field.

        Args:
            column_name: Model field name.

        Returns:
            str | None: Configured description, if any.
        """
        if not self.column_descriptions:
            return None
        return self.column_descriptions.get(column_name)

    def _get_default_form_columns(self):
        """Get default form columns.

        Returns:
            List of column names.
        """
        columns = []
        mapper = inspect(self.model)
        for p in mapper.attrs:
            if hasattr(p, "direction"):
                continue
            elif hasattr(p, "columns"):
                column = p.columns[0]
                if column.foreign_keys:
                    continue
                if column.primary_key:
                    continue
                columns.append(p.key)

        return columns
