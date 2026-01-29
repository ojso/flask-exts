import pytest
from flask_exts.admin import expose_url
from flask_exts.admin.view import View
from flask_exts.admin.action_mixin import ActionMixin


class MockView(View, ActionMixin):
    @expose_url("/")
    def index(self):
        return "Success!"

    @expose_url("/test/")
    def test(self):
        return self.render("mock.html")


def test_view():
    view = MockView()

    # print(view._urls)
    # print(view._default_view)
    assert len(view._urls) == 3
    assert ("/", "index", ("GET",)) in view._urls
    assert ("/test/", "test", ("GET",)) in view._urls
    assert ("/action/", "action_view", ("POST",)) in view._urls

    assert view._default_view == "index"
    assert view.name == "Mock View"
    assert view.endpoint == "mockview"
    assert view.url is None
    assert view.static_folder is None
    assert view.admin is None
    assert view.blueprint is None
