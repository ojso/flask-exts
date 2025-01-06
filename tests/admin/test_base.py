import pytest
from flask import url_for
from flask import abort
from flask import request
from flask.views import MethodView
from flask_exts.admin.wraps import expose, expose_plugview
from flask_exts.admin.view import BaseView
from flask_exts.admin.admin import Admin
from flask_exts.admin.menu import MenuLink

from ..funcs import print_app_endpoint_rule
from ..funcs import get_app_endpoint_rule


class MockView(BaseView):
    allow_access = True
    visible = True

    @expose("/")
    def index(self):
        return "Success!"

    @expose("/test/")
    def test(self):
        return self.render("mock.html")

    def is_accessible(self):
        if self.allow_access:
            return super().is_accessible()
        return False

    def is_visible(self):
        if self.visible:
            return super().is_visible()
        return False


class MockNoindexView(BaseView):
    allow_access = True
    visible = True

    @expose("/test/")
    def test(self):
        return self.render("mock.html")

    def is_accessible(self):
        if self.allow_access:
            return super().is_accessible()
        return False

    def is_visible(self):
        if self.visible:
            return super().is_visible()
        return False


class MockExtendView(MockView):
    @expose("/test2/")
    def test2(self):
        return self.render("mock.html")


class MockMethodView(BaseView):
    @expose("/")
    def index(self):
        return "Success!"

    @expose_plugview("/_api/1")
    class API1(MethodView):
        def get(self, cls):
            return cls.render("method.html", request=request, name="API1")

        def post(self, cls):
            return cls.render("method.html", request=request, name="API1")

        def put(self, cls):
            return cls.render("method.html", request=request, name="API1")

        def delete(self, cls):
            return cls.render("method.html", request=request, name="API1")

    @expose_plugview("/_api/2")
    class API2(MethodView):
        def get(self, cls):
            return cls.render("method.html", request=request, name="API2")

        def post(self, cls):
            return cls.render("method.html", request=request, name="API2")

    @expose_plugview("/_api/3")
    @expose_plugview("/_api/4")
    class DoubleExpose(MethodView):
        def get(self, cls):
            return cls.render("method.html", request=request, name="API3")


def test_baseview_defaults():
    view = MockView()
    assert view.name == "Mock View"
    assert view.endpoint == "mockview"
    assert view.url is None
    assert view.static_folder is None
    assert view.category is None
    assert view.admin is None
    assert view.blueprint is None


def test_admin_defaults():
    admin = Admin()
    assert admin.name == "Admin"
    assert admin.url == "/admin"
    assert admin.endpoint == "admin"
    assert admin.app is None

    # Check if default view was added
    assert len(admin._views) == 2
    assert admin._views[0] == admin.index_view
    assert admin._views[1] == admin.user_view

    # check index_view
    assert admin.index_view is not None
    assert admin.index_view.endpoint == "index"
    assert admin.index_view.url == "/"
    assert admin.index_view.index_template == "admin/index.html"

    # check user_view
    assert admin.user_view is not None
    assert admin.user_view.endpoint == "user"
    assert admin.user_view.url == "/user"
    assert admin.user_view.index_template == "admin/user/index.html"

def test_admin_init_app(app,client):
    admin = Admin()
    admin.init_app(app)

    assert "admin" in admin.app.extensions
    assert len(admin.app.extensions["admin"]) == 1
    assert admin.app.extensions["admin"][0] == admin

    # print(app.extensions)
    # print(app.blueprints)
    print_app_endpoint_rule(app)

    assert len(app.blueprints) == 3
    assert "template" in app.blueprints
    assert "index" in app.blueprints
    assert "user" in app.blueprints

    assert get_app_endpoint_rule(app, "index.index") == "/"
    assert get_app_endpoint_rule(app, "index.admin_index") == "/admin/"
    assert get_app_endpoint_rule(app, "user.index") == "/user/"
    assert get_app_endpoint_rule(app, "user.login") == "/user/login/"
    assert get_app_endpoint_rule(app, "user.logout") == "/user/logout/"
    assert get_app_endpoint_rule(app, "user.register") == "/user/register/"

    with app.test_request_context():
        index_index_url = url_for("index.index")
        admin_index_url = url_for("index.admin_index")
        user_index_url = url_for("user.index")
        user_login_url = url_for("user.login")
        user_logout_url = url_for("user.logout")
        user_register_url = url_for("user.register")

    assert index_index_url == "/"
    assert admin_index_url == "/admin/"
    assert user_index_url == "/user/"
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


def test_admin_raise():
    admin = Admin()
    admin = Admin(url="/")
    admin = Admin(url="/admin")
    with pytest.raises(Exception):
        admin = Admin(url="admin")


def test_admin_init_app_raise(app):
    admin = Admin()
    admin.init_app(app)
    with pytest.raises(Exception):
        admin.init_app(app)

def test_method_views(app):
    admin = Admin()
    admin.init_app(app)
    view = MockMethodView()
    admin.add_view(view)

    client = app.test_client()

    rv = client.get("/admin/mockmethodview/_api/1")
    assert rv.data == b"GET - API1"
    rv = client.put("/admin/mockmethodview/_api/1")
    assert rv.data == b"PUT - API1"
    rv = client.post("/admin/mockmethodview/_api/1")
    assert rv.data == b"POST - API1"
    rv = client.delete("/admin/mockmethodview/_api/1")
    assert rv.data == b"DELETE - API1"

    rv = client.get("/admin/mockmethodview/_api/2")
    assert rv.data == b"GET - API2"
    rv = client.post("/admin/mockmethodview/_api/2")
    assert rv.data == b"POST - API2"
    rv = client.delete("/admin/mockmethodview/_api/2")
    assert rv.status_code == 405
    rv = client.put("/admin/mockmethodview/_api/2")
    assert rv.status_code == 405

    rv = client.get("/admin/mockmethodview/_api/3")
    assert rv.data == b"GET - API3"
    rv = client.get("/admin/mockmethodview/_api/4")
    assert rv.data == b"GET - API3"

def test_admin_customizations(app, client):
    admin = Admin(app, name="Test", url="/foobar")
    assert admin.name == "Test"
    assert admin.url == "/foobar"
    # print(app.extensions)
    # print(app.blueprints)
    # print_app_endpoint_rule(app)
    # print(app.view_functions)

    # rv = client.get("/foobar/")
    # assert rv.status_code == 200


def test_permissions(app, client):
    admin = Admin()
    view = MockView()
    admin.add_view(view)
    admin.init_app(app)

    rv = client.get("/admin/")
    assert rv.status_code == 200

    rv = client.get("/admin/mockview/")
    assert rv.data == b"Success!"

    rv = client.get("/admin/mockview/test/")
    assert rv.data == b"Success!"

    # Check authentication failure
    view.allow_access = False
    rv = client.get("/admin/mockview/")
    assert rv.status_code == 403


def test_inaccessible_callback(app, client):
    admin = Admin()
    view = MockView()
    admin.add_view(view)
    admin.init_app(app)
    view.allow_access = False
    view.inaccessible_callback = lambda *args, **kwargs: abort(418)
    rv = client.get("/admin/mockview/")
    assert rv.status_code == 418

def test_admin_category():
    admin = Admin()
    admin.add_category("Category1", "class-name", "icon-type", "icon-value")
    view_1 = MockView(name="Test 1", endpoint="test1", category="Category1")
    view_2 = MockView(name="Test 2", endpoint="test2", category="Category2")
    view_3 = MockView(name="Test 3", endpoint="test3", category="Category2")

    admin.add_view(view_1)
    admin.add_view(view_2)
    admin.add_view(view_3)

    # print(admin.menu())
    # print(admin._menu_categories)
    # print(admin._menu_links)

    assert "Category1" in admin._menu_categories
    assert "Category2" in admin._menu_categories

    for menu in admin.menu():
        if menu.name == "Category1":
            menu_category1 = menu
        if menu.name == "Category2":
            menu_category2 = menu


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

def test_menu_links(app, client):
    admin = Admin()
    admin.init_app(app)
    admin.add_link(MenuLink("TestMenuLink1", endpoint=".index"))
    admin.add_link(MenuLink("TestMenuLink2", url="http://python.org/"))
    rv = client.get("/admin/")
    data = rv.get_data(as_text=True)
    # print(data)
    assert "TestMenuLink1" in data
    assert "TestMenuLink2" in data
