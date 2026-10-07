from flask import request


class ViewArgs:
    """List view arguments."""

    def __init__(
        self,
        page=0,
        page_size=0,
        sort=None,
        sort_desc=False,
        search=None,
        filters=None,
        extra_args=None,
    ):
        self.page = page
        self.page_size = page_size
        self.sort = sort
        self.sort_desc = sort_desc
        self.search = search
        self.filters = filters or []
        self.extra_args = extra_args or {}

    def clone(self, **kwargs):
        """Return a copy of the current view arguments with overrides."""
        args = {
            "page": self.page,
            "page_size": self.page_size,
            "sort": self.sort,
            "sort_desc": self.sort_desc,
            "search": self.search,
            "filters": self.filters,
            "extra_args": self.extra_args.copy(),
        }
        args.update(kwargs)
        return ViewArgs(**args)


class PaginationMixin:
    """Mixin that provides pagination state and URL generation for list views."""

    # Pagination settings
    page_size: int = 20
    """
        Default page size for pagination.
    """

    can_set_page_size = True
    """
        Allows to select page size via dropdown list
    """

    page_size_options: tuple = (5, 10, 20, 50, 100)
    """
        Sets the page size options available, if `can_set_page_size` is True
    """

    def get_safe_page_size(self, page_size: int) -> int:
        """Return a validated page size for the current view.

        Args:
            page_size: Requested page size.

        Returns:
            int: The validated page size.
        """
        if self.can_set_page_size and page_size in self.page_size_options:
            return page_size
        return self.page_size

    def _get_list_args(self) -> "ViewArgs":
        """Return the current list arguments parsed from the request.

        Returns:
            ViewArgs: A container with page, sort, search, and filter settings.
        """
        return ViewArgs(
            page=request.args.get("page", 0, type=int),
            page_size=request.args.get("page_size", 0, type=int),
            sort=request.args.get("sort", None, type=int),
            sort_desc=request.args.get("desc", None, type=int),
            search=request.args.get("search", None),
            filters=self.get_active_filters()
            if hasattr(self, "get_active_filters")
            else [],
            extra_args={
                k: v
                for k, v in request.args.items()
                if k
                not in (
                    "page",
                    "page_size",
                    "sort",
                    "desc",
                    "search",
                    "url",
                )
                and not k.startswith("flt")
            },
        )

    def _get_list_url(self, view_args: "ViewArgs") -> str:
        """Generate a list-view URL from the current view arguments.

        Args:
            view_args: Parsed pagination and filtering state.

        Returns:
            str: URL for the current page state.
        """
        page = view_args.page or None
        desc = 1 if view_args.sort_desc else None

        kwargs = {
            "page": page,
            "sort": view_args.sort,
            "desc": desc,
            "search": view_args.search,
        }
        kwargs.update(view_args.extra_args)

        kwargs["page_size"] = self.get_safe_page_size(view_args.page_size)

        if hasattr(self, "get_active_filters_kwargs"):
            kwargs.update(self.get_active_filters_kwargs(view_args.filters))

        if hasattr(self, "get_url"):
            return self.get_url(".index_view", **kwargs)
        else:
            return f"?{'&'.join(f'{k}={v}' for k, v in kwargs.items() if v)}"
