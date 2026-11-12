from urllib.parse import parse_qs, urlsplit

from flask_exts.admin.model.handlers.pagination import PaginationHandler, ViewArgs


class FakeView:
    page_size = 20
    can_set_page_size = True
    page_size_options = (10, 20, 50)

    def __init__(self):
        self.filters_kwargs = {}

    def get_url(self, endpoint):
        assert endpoint == ".index_view"
        return "/admin/example/"

    def get_active_filters_kwargs(self, filters):
        return dict(self.filters_kwargs)


def test_get_list_url_without_parameters():
    view = FakeView()
    view.page_size = 0
    handler = PaginationHandler(view)

    assert handler.get_list_url(ViewArgs()) == "/admin/example/"


def test_get_list_url_omits_first_page():
    handler = PaginationHandler(FakeView())

    assert handler.get_list_url(ViewArgs(page=1, page_size=20)) == (
        "/admin/example/?page_size=20"
    )


def test_get_list_url_encodes_special_characters():
    handler = PaginationHandler(FakeView())
    assert not hasattr(handler, "get_url")

    url = handler.get_list_url(
        ViewArgs(
            page=2,
            page_size=20,
            sort=0,
            sort_desc=True,
            search="a b&c",
        )
    )

    assert url.startswith("/admin/example/?")
    assert parse_qs(urlsplit(url).query) == {
        "page": ["2"],
        "page_size": ["20"],
        "sort": ["0"],
        "desc": ["1"],
        "search": ["a b&c"],
    }


def test_get_list_url_encodes_extra_args_and_filters():
    view = FakeView()
    view.filters_kwargs = {"flt0_0": "x&y"}
    handler = PaginationHandler(view)

    url = handler.get_list_url(
        ViewArgs(
            page_size=20,
            filters=[(0, "integer_value", "x&y")],
            extra_args={"foo": "a b"},
        )
    )

    params = parse_qs(urlsplit(url).query)
    assert params["foo"] == ["a b"]
    assert params["flt0_0"] == ["x&y"]
