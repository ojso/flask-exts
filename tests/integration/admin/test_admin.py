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


def test_portal_index_page_shows_quick_start(app, client):
    rv = client.get("/")

    assert rv.status_code == 200
    html = rv.get_data(as_text=True)
    assert "Flask-Exts" in html
    assert "Quick start" in html
    assert "pip install flask-exts" in html
    assert 'href="/admin/"' in html


def test_admin_navbar_language_selector_uses_config(app, client, admin, login_as_admin):
    with app.app_context():
        login_as_admin()
    app.config["BABEL_ACCEPT_LANGUAGES"] = "en;zh"

    rv = client.get("/admin/")

    assert rv.status_code == 200
    html = rv.get_data(as_text=True)
    assert 'href="/admin/?lang=en"' in html
    assert 'href="/admin/?lang=zh"' in html
    assert "English" in html
    assert "中文" in html
    assert "🌐" in html
    assert "?lang=fr" not in html


def test_admin_navbar_language_selector_needs_multiple_languages(
    app, client, admin, login_as_admin
):
    with app.app_context():
        login_as_admin()
    app.config["BABEL_ACCEPT_LANGUAGES"] = "en"

    rv = client.get("/admin/")

    assert rv.status_code == 200
    assert "?lang=" not in rv.get_data(as_text=True)


def test_admin_navbar_language_selector_switches_locale(
    app, client, admin, login_as_admin
):
    with app.app_context():
        login_as_admin()
    app.config["BABEL_ACCEPT_LANGUAGES"] = "en;zh"

    rv = client.get("/admin/?lang=zh")

    assert rv.status_code == 200
    assert '<html lang="zh">' in rv.get_data(as_text=True)


def test_admin_navbar_language_selector_preserves_query(
    app, client, admin, login_as_admin
):
    with app.app_context():
        login_as_admin()
    app.config["BABEL_ACCEPT_LANGUAGES"] = "en;zh"

    rv = client.get("/admin/?foo=1&foo=2&lang=zh")

    assert rv.status_code == 200
    assert "foo=1&amp;foo=2&amp;lang=en" in rv.get_data(as_text=True)


def test_inactive_admin_is_denied(app, client, admin, login_as_admin):
    mock_view = MockView()
    admin.register_view(mock_view)

    with app.app_context():
        user = login_as_admin()
        current_userstore.user_set(user, is_active=False)

    rv = client.get("/admin/mockview/")
    assert rv.status_code == 403
