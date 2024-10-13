import pytest
from flask import url_for
from flask import abort
from flask import request
from flask.views import MethodView
from flask_exts.admin.wraps import expose, expose_plugview
from flask_exts.admin.view import BaseView
from flask_exts.admin.admin import Admin
from flask_exts.admin.menu import MenuLink
from flask_exts.admin.admin_index_view import AdminIndexView

from ..funcs import print_app_endpoint_rule
from ..funcs import get_app_endpoint_rule


class MockView(BaseView):
    # Various properties
    allow_call = True
    allow_access = True
    visible = True

    @expose("/")
    def index(self):
        return "Success!"

    @expose("/test/")
    def test(self):
        return self.render("mock.html")

    def _handle_view(self, name, **kwargs):
        if self.allow_call:
            return super()._handle_view(name, **kwargs)
        else:
            return "Failure!"

    def is_accessible(self):
        if self.allow_access:
            return super().is_accessible()

        return False

    def is_visible(self):
        if self.visible:
            return super().is_visible()

        return False


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
    assert view.category is None
    assert view.endpoint == "mockview"
    assert view.url is None
    assert view.static_folder is None
    assert view.admin is None
    assert view.blueprint is None


def test_admin_defaults():
    admin = Admin()
    assert admin.name == "Admin"
    assert admin.url == "/admin"
    assert admin.endpoint == "admin"
    assert admin.app is None
    assert admin.index_view is not None
    assert admin.index_view.endpoint == "admin"
    assert admin.index_view.url == "/admin"
    assert admin.index_view.static_folder == "../static"
    assert admin.index_view._index_template == "admin/index.html"
    # Check if default view was added
    assert len(admin._views) == 1
    assert admin._views[0] == admin.index_view
    #
    # print(admin.index_view._urls)


def test_admin_init_error():
    admin = Admin()
    admin = Admin(url="/")
    admin = Admin(url="/admin")
    with pytest.raises(Exception):
        admin = Admin(url="admin")


def test_double_init(app):
    admin = Admin()
    admin.init_app(app)
    with pytest.raises(Exception):
        admin.init_app(app)


def test_nested_flask_views(app):
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


def test_app_admin_defaults(app):
    admin = Admin()
    admin.init_app(app)

    assert "admin" in admin.app.extensions
    assert len(admin.app.extensions["admin"]) == 1
    assert admin.app.extensions["admin"][0] == admin

    # print(app.extensions)
    # print(app.blueprints)

    #
    # for k in rules:
    # print(k.endpoint, k.rule)


def test_admin_view(app, client):
    admin = Admin()
    admin.init_app(app)
    mock_view = MockView()
    admin.add_view(mock_view)

    assert "admin" in admin.app.extensions
    assert len(admin.app.extensions["admin"]) == 1
    assert admin.app.extensions["admin"][0] == admin

    # print(app.extensions)
    # print(app.blueprints)

    # print_app_endpoint_rule(app)
    assert get_app_endpoint_rule(app, "admin.static") == "/admin/static/<path:filename>"

    with app.test_request_context():
        logo_url = url_for("admin.static", filename="logo.png")
    assert logo_url == "/admin/static/logo.png"
    rv = client.get(logo_url)
    assert rv.status_code == 200


def test_root_admin_view(app, client):
    admin = Admin(url="/")
    admin.init_app(app)
    mock_view = MockView()
    admin.add_view(mock_view)

    assert "admin" in admin.app.extensions
    assert len(admin.app.extensions["admin"]) == 1
    assert admin.app.extensions["admin"][0] == admin
    assert get_app_endpoint_rule(app, "admin.static") == "/admin/static/<path:filename>"
    with app.test_request_context():
        logo_url = url_for("admin.static", filename="logo.png")
    assert logo_url == "/admin/static/logo.png"
    rv = client.get(logo_url)
    assert rv.status_code == 200


def test_admin_customizations(app):
    admin = Admin(app, name="Test", url="/foobar", static_url_path="/static/my/admin")
    assert admin.name == "Test"
    assert admin.url == "/foobar"
    # print(app.extensions)
    # print(app.blueprints)

    # print(app.view_functions)

    with app.test_client() as client:
        rv = client.get("/foobar/")
    assert rv.status_code == 200


def test_call(app, client):
    admin = Admin()
    view = MockView()
    admin.add_view(view)
    admin.init_app(app)
    client = app.test_client()

    rv = client.get("/admin/")
    assert rv.status_code == 200

    rv = client.get("/admin/mockview/")
    assert rv.data == b"Success!"

    rv = client.get("/admin/mockview/test/")
    assert rv.data == b"Success!"

    # Check authentication failure
    view.allow_call = False
    rv = client.get("/admin/mockview/")
    assert rv.data == b"Failure!"


def test_permissions(app, client):
    admin = Admin()
    view = MockView()
    admin.add_view(view)
    admin.init_app(app)
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


def test_visibility(app, client):
    admin = Admin()
    admin.init_app(app)
    view = MockView(name="TestMenuItem")
    view.visible = False
    admin.add_view(view)
    rv = client.get("/admin/mockview/")
    assert "TestMenuItem" not in rv.data.decode("utf-8")


def test_add_category():
    admin = Admin()
    admin.add_category("Category1", "class-name", "icon-type", "icon-value")
    admin.add_view(MockView(name="Test 1", endpoint="test1", category="Category1"))
    admin.add_view(MockView(name="Test 2", endpoint="test2", category="Category2"))

    # print(admin._menu)
    # print(admin._menu_categories)
    # print(admin._menu_links)

    assert len(admin.menu()) == 3

    # Test 1 should be underneath Category1
    assert admin.menu()[1].name == "Category1"
    assert admin.menu()[1].get_class_name() == "class-name"
    assert admin.menu()[1].get_icon_type() == "icon-type"
    assert admin.menu()[1].get_icon_value() == "icon-value"
    assert len(admin.menu()[1].get_children()) == 1
    assert admin.menu()[1].get_children()[0].name == "Test 1"

    # Test 2 should be underneath Category2
    assert admin.menu()[2].name == "Category2"
    assert admin.menu()[2].get_class_name() is None
    assert admin.menu()[2].get_icon_type() is None
    assert admin.menu()[2].get_icon_value() is None
    assert len(admin.menu()[2].get_children()) == 1
    assert admin.menu()[2].get_children()[0].name == "Test 2"


def test_submenu():
    admin = Admin()
    admin.add_view(MockView(name="Test 1", category="Test", endpoint="test1"))

    # Second view is not normally accessible
    view = MockView(name="Test 2", category="Test", endpoint="test2")
    view.allow_access = False
    admin.add_view(view)

    assert "Test" in admin._menu_categories
    assert len(admin._menu) == 2
    assert admin._menu[1].name == "Test"
    assert len(admin._menu[1]._children) == 2

    # Categories don't have URLs
    assert admin._menu[1].get_url() is None

    # Categories are only accessible if there is at least one accessible child
    assert admin._menu[1].is_accessible()

    children = admin._menu[1].get_children()
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