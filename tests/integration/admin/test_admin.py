from flask import url_for

from flask_exts.admin import View, expose_url
from flask_exts.proxies import current_userstore


class MockView(View):
    @expose_url("/")
    def index(self):
        return "Success!"

    @expose_url("/test/")
    def test(self):
        return "Test!"


def test_app_admin_register_view(app, client, admin, login_as_admin):
    mock_view = MockView()
    admin.register_view(mock_view)
    assert "mockview" in app.blueprints

    with app.test_request_context():
        mock_index_url = url_for("mockview.index")
        mock_test_url = url_for("mockview.test")

    assert mock_index_url == "/admin/mockview/"
    assert mock_test_url == "/admin/mockview/test/"

    with app.app_context():
        login_as_admin()

    rv = client.get(mock_index_url)
    assert rv.status_code == 200
    assert rv.text == "Success!"

    rv = client.get(mock_test_url)
    assert rv.status_code == 200
    assert rv.text == "Test!"


def test_inactive_admin_is_denied(app, client, admin, login_as_admin):
    mock_view = MockView()
    admin.register_view(mock_view)

    with app.app_context():
        user = login_as_admin()
        current_userstore.user_set(user, is_active=False)

    rv = client.get("/admin/mockview/")
    assert rv.status_code == 403
