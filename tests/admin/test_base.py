import pytest
from flask import url_for
from flask_exts.admin import expose
from flask_exts.admin import BaseView
from flask_exts.admin.admin import Admin
from flask_exts.admin.menu import MenuLink

from ..helper import print_app_endpoint_rule
from ..helper import get_app_endpoint_rule


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


class MockNoindexView(BaseView):
    allow_access = True

    @expose("/test/")
    def test(self):
        return self.render("mock.html")

    def is_accessible(self):
        if self.allow_access:
            return super().is_accessible()
        return False


def test_baseview_default():
    view = MockView()
    assert view.name == "Mock View"
    assert view.endpoint == "mockview"
    assert view.url is None
    assert view.static_folder is None
    assert view.admin is None
    assert view.blueprint is None


def test_admin_default():
    admin = Admin()
    # print(admin.name)
    # print(admin.url)
    # print(admin.endpoint)
    # print(admin._views)
    # print(admin.menu)
    assert admin.name == "Admin"
    assert admin.url == "/admin"
    assert admin.endpoint == "admin"


def test_admin_menu():
    admin = Admin()
    menu = admin.menu
    assert menu.admin == admin
    menu.add_category("Category1", "class-name", "icon-type", "icon-value")
    view_1 = MockView(name="Test 1", endpoint="test1")
    view_2 = MockView(name="Test 2", endpoint="test2")
    view_3 = MockView(name="Test 3", endpoint="test3")

    admin.add_view(view_1, category="Category1")
    admin.add_view(view_2, category="Category2")
    admin.add_view(view_3, category="Category2")

    # print(menu._menu)
    # print(menu._menu_categories)
    # print(menu._menu_links)

    assert "Category1" in menu._menu_categories
    assert "Category2" in menu._menu_categories

    for m in menu.menus():
        if m.name == "Category1":
            menu_category1 = m
        if m.name == "Category2":
            menu_category2 = m

    assert menu_category1.get_class_name() == "class-name"
    assert menu_category1.get_icon_type() == "icon-type"
    assert menu_category1.get_icon_value() == "icon-value"
    assert len(menu_category1.get_children()) == 1
    assert menu_category1.get_children()[0].name == "Test 1"

    assert menu_category2.get_class_name() is None
    assert menu_category2.get_icon_type() is None
    assert menu_category2.get_icon_value() is None
    assert len(menu_category2.get_children()) == 2
    assert menu_category2.get_children()[0].name == "Test 2"
    assert menu_category2.get_children()[1].name == "Test 3"

    # Categories don't have URLs
    assert menu_category1.get_url() is None
    assert menu_category2.get_url() is None

    view_3.allow_access = False
    # Categories are only accessible if there is at least one accessible child
    assert menu_category2.is_accessible()
    children = menu_category2.get_children()
    assert len(children) == 1
    assert children[0].is_accessible()


def test_app_admin_add_view(app, client, admin: Admin):
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


def test_menu_links(client, admin):
    menu = admin.menu
    menu.add_link(MenuLink("TestMenuLink1", endpoint=".index"))
    menu.add_link(MenuLink("TestMenuLink2", url="http://python.org/"))
    
    rv = client.get("/admin/")
    assert "TestMenuLink1" in rv.text
    assert "TestMenuLink2" in rv.text
