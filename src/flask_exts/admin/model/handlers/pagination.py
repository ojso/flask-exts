from urllib.parse import urlencode

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

    def __str__(self):
        filters = ", ".join(repr(f) for f in self.filters)
        extra = ", ".join(f"{k}={v!r}" for k, v in self.extra_args.items())
        return (
            f"{type(self).__name__}("
            f"page={self.page}, "
            f"page_size={self.page_size}, "
            f"sort={self.sort!r}, "
            f"sort_desc={self.sort_desc}, "
            f"search={self.search!r}, "
            f"filters=[{filters}], "
            f"extra_args={{{extra}}}"
            f")"
        )


class PaginationHandler:
    """Handler that provides pagination state and URL generation for list views."""

    def __init__(self, view):
        self.view = view
        self.page_size = view.page_size
        self.can_set_page_size = view.can_set_page_size
        self.page_size_options = view.page_size_options

    def get_default_page_size(self):
        return self.page_size

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

    def get_list_args(self) -> "ViewArgs":
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
            filters=self.view.get_active_filters(),
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

    def get_list_url(self, view_args: "ViewArgs") -> str:
        """Generate an encoded list-view URL from the current view arguments.

        Args:
            view_args: Parsed pagination and filtering state.

        Returns:
            str: URL for the current page state with safely encoded parameters.
        """
        params = {}

        if view_args.page and view_args.page > 1:
            params["page"] = view_args.page

        page_size = self.get_safe_page_size(view_args.page_size)
        if page_size:
            params["page_size"] = page_size

        if view_args.sort is not None:
            params["sort"] = view_args.sort

        if view_args.sort_desc:
            params["desc"] = 1

        if view_args.search:
            params["search"] = view_args.search

        params.update(view_args.extra_args)
        params.update(self.view.get_active_filters_kwargs(view_args.filters))

        query_str = urlencode(params, doseq=True)
        base_url = self.view.get_url(".index_view")
        return f"{base_url}?{query_str}" if query_str else base_url
