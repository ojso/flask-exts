import pytest


def test_exts_extensions(exts):
    registries = exts._registry.get_all()
    assert len(registries) == 10
    registry_names = [r.name for r in registries]
    # print(registry_names)
    assert "database" in registry_names
    assert "babel" in registry_names
    assert "html" in registry_names
    assert "email" in registry_names
    assert "usercenter" in registry_names
    assert "login" in registry_names
    assert "security" in registry_names
    assert "admin" in registry_names
    assert "startup" in registry_names


def test_blueprints(app):
    assert len(app.blueprints) == 3
    assert "_template" in app.blueprints
    assert "index" in app.blueprints
    assert "user" in app.blueprints


def test_jinja_globals(app):
    assert "_template" in app.jinja_env.globals
    assert "csrf_token" in app.jinja_env.globals


@pytest.mark.skip(reason="not print.")
def test_prints(app):
    from .helper import print_blueprints
    from .helper import print_routes

    print_blueprints(app)
    print_routes(app)
