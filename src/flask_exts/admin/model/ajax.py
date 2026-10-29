DEFAULT_PAGE_SIZE = 10


class AjaxModelLoader:
    """Ajax related model loader."""

    def __init__(self, name, options):
        self.name = name
        self.options = options

    def format(self, model):
        """Return (id, name) tuple from the model."""
        raise NotImplementedError()

    def get_one(self, pk):
        """Get model by its primary key.

        Args:
            pk: Primary key value
        """
        raise NotImplementedError()

    def get_list(self, query, offset=0, limit=DEFAULT_PAGE_SIZE):
        """Return models that match `query`.

        Args:
            query: Query string
            offset: Offset
            limit: Limit
        """
        raise NotImplementedError()
