import pytest
from flask import url_for
from flask_exts.admin import expose
from flask_exts.admin import BaseView


class MockView(BaseView):
    allow_access = True

    @expose("/")
    def index(self):
        return "Success!"

    @expose("/test/")
    def test(self):
        return self.render("mock.html")

    def allow(self, *args, **kwargs):
        return self.allow_access


def test_app_admin_default(app, client, admin):
    # print(app.blueprints)

    # Check if default view was added
    assert len(admin._views) == 2
    assert "index" in app.blueprints
    assert "user" in app.blueprints

    index_view = admin._views["index"]
    user_view = admin._views["user"]

    # check index_view
    assert index_view is not None
    assert index_view.endpoint == "index"
    assert index_view.url == "/"

    # check user_view
    assert user_view is not None
    assert user_view.endpoint == "user"
    assert user_view.url == "/user"
    assert user_view.index_template == "views/user/index.html"

    with app.test_request_context():
        index_index_url = url_for("index.index")
        admin_index_url = url_for("index.admin_index")
        user_index_url = url_for("user.index")
        user_login_url = url_for("user.login")
        user_logout_url = url_for("user.logout")
        user_register_url = url_for("user.register")

    assert index_index_url == "/"
    assert admin_index_url == "/admin/"
    assert user_index_url == "/user/index/"
    assert user_login_url == "/user/login/"
    assert user_logout_url == "/user/logout/"
    assert user_register_url == "/user/register/"

    rv = client.get(index_index_url)
    assert rv.status_code == 200
    rv = client.get(admin_index_url)
    assert rv.status_code == 200
    rv = client.get(user_index_url)
    assert rv.status_code == 302
    rv = client.get(user_login_url)
    assert rv.status_code == 200
    rv = client.get(user_register_url)
    assert rv.status_code == 200
    rv = client.get(user_logout_url)
    assert rv.status_code == 302


def test_app_admin_add_view(app, client, admin):
    mock_view = MockView()
    admin.add_view(mock_view)
    assert "mockview" in app.blueprints

    with app.test_request_context():
        mock_index_url = url_for("mockview.index")
        mock_test_url = url_for("mockview.test")

    assert mock_index_url == "/admin/mockview/"
    assert mock_test_url == "/admin/mockview/test/"

    rv = client.get(mock_index_url)
    assert rv.status_code == 200
    assert rv.text == "Success!"

    rv = client.get(mock_test_url)
    assert rv.status_code == 200
    assert rv.text == "Success!"

    # Check authentication failure
    mock_view.allow_access = False
    rv = client.get("/admin/mockview/")
    assert rv.status_code == 403
