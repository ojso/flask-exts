from typing import Tuple, List, Any, Optional


class ReadOperationsMixin:
    """Mixin for reading model records and paginated list data."""

    def get_list(
        self,
        page: int,
        sort_field: Optional[str],
        sort_desc: bool,
        search: Optional[str],
        filters: List[Tuple],
        page_size: Optional[int] = None,
    ) -> Tuple[Optional[int], List[Any]]:
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
            Tuple[Optional[int], List[Any]]: ``(count, rows)``. The count may be
                ``None`` when it cannot be determined.

        Raises:
            NotImplementedError: If the subclass does not implement the hook.
        """
        raise NotImplementedError("Please implement get_list method")

    def get_one(self, id: Any) -> Optional[Any]:
        """Return a single model by its identifier.

        Args:
            id: Model identifier.

        Returns:
            Optional[Any]: The model instance, or ``None`` when no record matches.

        Raises:
            NotImplementedError: If the subclass does not implement this hook.
        """
        raise NotImplementedError("Please implement get_one method")

    def get_pk_value(self, obj: Any) -> Any:
        """
        Return PK value from a model object.
        """
        raise NotImplementedError("Please implement get_pk_value method")
