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

    def __init__(self, model, **kwargs):
        """Initialize inline form settings for a model.

        Args:
            model: Model class.
            kwargs: Additional options.
        """
        self.model = model

        for k, v in kwargs.items():
            setattr(self, k, v)

        if self.form_columns is None:
            self.form_columns = self._get_default_form_columns()

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
