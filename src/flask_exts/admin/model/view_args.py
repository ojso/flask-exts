class ViewArgs:
    """
    List view arguments.
    """

    def __init__(
        self,
        page=None,
        page_size=None,
        sort=None,
        sort_desc=None,
        search=None,
        filters=None,
        extra_args=None,
    ):
        self.page = page
        self.page_size = page_size
        self.sort = sort
        self.sort_desc = bool(sort_desc)
        self.search = search
        self.filters = filters

        if not self.search:
            self.search = None

        self.extra_args = extra_args or dict()

    def clone(self, **kwargs):
        if self.filters:
            flt = list(self.filters)
        else:
            flt = None

        kwargs.setdefault("page", self.page)
        kwargs.setdefault("page_size", self.page_size)
        kwargs.setdefault("sort", self.sort)
        kwargs.setdefault("sort_desc", self.sort_desc)
        kwargs.setdefault("search", self.search)
        kwargs.setdefault("filters", flt)
        kwargs.setdefault("extra_args", dict(self.extra_args))

        return ViewArgs(**kwargs)
