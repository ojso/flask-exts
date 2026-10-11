from flask import url_for


def test_app_extensions(app):
    # print(app.extensions)
    # print(app.extensions.keys())
    assert "exts" in app.extensions
    assert "babel" in app.extensions
    assert "flask_exts_sqla" in app.extensions


def test_exts_extensions(exts):
    registries = exts.list_extensions()
    assert len(registries) == 10
    registry_names = [r.name for r in registries]
    # print(registry_names)
    assert "database" in registry_names
    assert "babel" in registry_names
    assert "frontend" in registry_names
    assert "emailer" in registry_names
    assert "usercenter" in registry_names
    assert "userstore" in registry_names
    assert "login" in registry_names
    assert "security" in registry_names
    assert "admin" in registry_names
    assert "portal" in registry_names

    assert registry_names.index("database") < registry_names.index("userstore")


def test_jinja_globals(app):
    assert "_template" in app.jinja_env.globals
    assert "csrf_token" in app.jinja_env.globals


def test_blueprints(app):
    assert len(app.blueprints) == 3
    assert "_template" in app.blueprints
    assert "index" in app.blueprints
    assert "user" in app.blueprints


def test_prints(app):
    # from .helper import print_blueprints, print_routes

    # print_blueprints(app)
    # print_routes(app)

    with app.test_request_context():
        assert url_for("index.index") is not None
        assert url_for("index.adminindex") is not None
        assert url_for("user.index") is not None
        assert url_for("user.login") is not None
        assert url_for("user.logout") is not None
        assert url_for("user.change_password") is not None
