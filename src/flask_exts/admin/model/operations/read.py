from typing import Any


class ReadOperationsMixin:
    """Mixin for reading model records and paginated list data."""

    def get_list(
        self,
        page: int,
        sort_field: str | None,
        sort_desc: bool,
        search: str | None,
        filters: list[tuple],
        page_size: int | None = None,
    ) -> tuple[int | None, list]:
        """Return a page of models from the data source.

        This method must be implemented by the subclass.

        Args:
            page: Zero-based page number.
            sort_field: Name of the sort column, or ``None``.
            sort_desc: Whether sorting is in descending order.
            search: Search query string.
            filters: List of filter tuples. Each tuple contains the field name
                and a filter value.
            page_size: Number of results per page. Set to ``0`` or ``False`` to
                disable the page-size limit.

        Returns:
            tuple[int | None, list[Any]]: ``(count, rows)``. The count may be
                ``None`` when it cannot be determined.

        Raises:
            NotImplementedError: If the subclass does not implement the hook.
        """
        raise NotImplementedError("Please implement get_list method")

    def get_one(self, id: Any) -> Any:
        """Return a single model by its identifier.

        Args:
            id: Model identifier.

        Returns:
            Any: The model instance, or ``None`` when no record matches.

        Raises:
            NotImplementedError: If the subclass does not implement this hook.
        """
        raise NotImplementedError("Please implement get_one method")

    def get_pk_value(self, obj: Any) -> Any:
        """
        Return PK value from a model object.
        """
        raise NotImplementedError("Please implement get_pk_value method")
