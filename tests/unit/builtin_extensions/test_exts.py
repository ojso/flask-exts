def test_app_extensions(app):
    # print(app.extensions)
    # print(app.extensions.keys())
    assert "exts" in app.extensions
    assert "babel" in app.extensions
    assert "flask_exts_sqla" in app.extensions


def test_exts_extensions(app):
    exts = app.extensions["exts"]
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
