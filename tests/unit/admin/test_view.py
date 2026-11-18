import pytest

from flask_exts.admin import View, expose_url


class MockView(View):
    @expose_url("/")
    def index(self):
        return "Success!"

    @expose_url("/test/")
    def test(self):
        return "test"


def test_view():
    view = MockView()
    # print(view._urls)
    # print(view._default_view)
    assert len(view._urls) == 2
    assert ("/", "index", ("GET",)) in view._urls
    assert ("/test/", "test", ("GET",)) in view._urls
    assert view._default_view == "index"

    assert view.name == "Mock View"
    assert view.endpoint == "mockview"
    assert view.url is None
    assert view.static_folder is None
    assert view.admin is None
    assert view.blueprint is None


class MultipleIndexView(View):
    @expose_url("/")
    def index(self):
        return "index"

    @expose_url("/")
    def z_index(self):
        return "z_index"


def test_first_exposed_index_view_is_the_default():
    view = MultipleIndexView()

    assert view._default_view == "index"


class LoginRequiredView(View):
    allow_access = True
    login_required_functions = ("index",)

    @expose_url("/")
    def index(self):
        return "index"

    @expose_url("/open/")
    def open(self):
        return "open"


def test_login_required_functions_are_kept_on_the_view():
    view = LoginRequiredView()

    assert view.login_required_functions == ("index",)
    assert view.allow_access is True


def test_login_required_functions_must_be_exposed():
    class BrokenView(View):
        login_required_functions = ("index", "missing")

        @expose_url("/")
        def index(self):
            return "index"

    with pytest.raises(ValueError, match="not exposed: missing"):
        BrokenView()


def test_login_required_functions_reject_a_bare_string():
    class BrokenView(View):
        login_required_functions = "index"

        @expose_url("/")
        def index(self):
            return "index"

    with pytest.raises(TypeError, match="not a string"):
        BrokenView()
