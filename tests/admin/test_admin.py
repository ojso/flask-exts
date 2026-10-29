from flask import url_for

from flask_exts.admin import Admin, View, expose_url
from flask_exts.admin.menu import MenuEndpoint, MenuLink


class MockView(View):
    @expose_url("/")
    def index(self):
        return "Success!"

    @expose_url("/test/")
    def test(self):
        return self.render("mock.html")


def test_admin_views():
    admin = Admin()
    # print(admin.menu)
    assert admin.name == "Admin"
    assert admin.url == "/admin"
    assert admin.endpoint == "admin"
    assert len(admin.get_views()) == 0

    # register a view
    mock_view = MockView()
    admin.register_view(mock_view)
    assert "mockview" in admin._views
    assert len(admin.get_views()) == 1


def test_admin_menu():
    admin = Admin()
    menu = admin.menu
    assert menu.admin is admin

    view_1 = MockView(name="test1", endpoint="test1")
    view_2 = MockView(name="test2", endpoint="test2")
    view_3 = MockView(name="test3", endpoint="test3")

    category1 = menu.add_category("Category1")
    category2 = menu.add_category("Category2")
    admin.register_view(view_1, category=category1)
    admin.register_view(view_2, category=category2)
    admin.register_view(view_3, category=category2)

    assert len(category1.get_children()) == 1
    assert category1.get_children()[0].name == "test1"

    assert len(category2.get_children()) == 2
    assert category2.get_children()[0].name == "test2"
    assert category2.get_children()[1].name == "test3"

    # Categories don't have URLs
    assert category1.get_url() is None
    assert category2.get_url() is None

    menu.add_menu_item(MenuEndpoint("TestMenuLink1", endpoint=".index"))
    menu.add_menu_item(MenuLink("TestMenuLink2", url="http://python.org/"))


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
    assert rv.text == "Success!"
