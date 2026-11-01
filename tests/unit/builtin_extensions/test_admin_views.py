from flask import url_for


def get_app_endpoint_rule(app, endpoint):
    rules = list(app.url_map.iter_rules())
    for k in rules:
        if k.endpoint == endpoint:
            return k.rule


def print_app_endpoint_rule(app):
    rules = list(app.url_map.iter_rules())
    for k in rules:
        print(k.endpoint, k.rule)


def print_blueprints(app):
    print("\n===== app.blueprints =====")
    # print(app.blueprints)
    for k, v in app.blueprints.items():
        print(k, v, v.static_folder)


def print_routes(app):
    print("\n===== app.url_map =====")
    rules = list(app.url_map.iter_rules())
    for k in rules:
        print(k.endpoint, k.rule, app.view_functions[k.endpoint])
    # for k in rules:
    #     print(k.rule, k.endpoint)
    # for k,v in app.view_functions.items():
    #     print(k, v)


def test_blueprints(app):
    assert len(app.blueprints) == 3
    assert "_template" in app.blueprints
    assert "index" in app.blueprints
    assert "user" in app.blueprints


def test_app_admin_default(app):
    admin = app.extensions["exts"].get_extension("admin").get_admin()
    assert len(admin.get_views()) == 2
    index_view = admin.get_view("index")
    user_view = admin.get_view("user")

    # check index_view
    assert index_view is not None
    assert index_view.endpoint == "index"
    assert index_view.url == "/"

    # check user_view
    assert user_view is not None
    assert user_view.endpoint == "user"
    assert user_view.url == "/user"
    assert user_view.index_template == "user/index.html"

    assert "index" in app.blueprints
    assert "user" in app.blueprints

    with app.test_request_context():
        index_index_url = url_for("index.index")
        index_admin_url = url_for("index.adminindex")
        user_index_url = url_for("user.index")
        user_login_url = url_for("user.login")
        user_logout_url = url_for("user.logout")
        user_register_url = url_for("user.register")

    assert index_index_url == "/"
    assert index_admin_url == "/admin/"
    assert user_index_url == "/user/index/"
    assert user_login_url == "/user/login/"
    assert user_logout_url == "/user/logout/"
    assert user_register_url == "/user/register/"
