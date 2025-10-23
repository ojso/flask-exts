import pytest
from .helper import print_blueprints
from .helper import print_routes


def test_extensions(app):
    # print(app.extensions)
    # print(app.extensions.keys())
    assert "babel" in app.extensions
    assert "sqlalchemy" in app.extensions
    assert getattr(app, "login_manager", None) is not None
    assert "manager" in app.extensions
    assert len(app.blueprints) == 3
    assert "_template" in app.blueprints
    assert "index" in app.blueprints
    assert "user" in app.blueprints
    assert "_template" in app.jinja_env.globals    
    manager = app.extensions["manager"]
    assert manager.usercenter is not None
    assert manager.security is not None
    assert manager.admin is not None
    admin = manager.admin
    assert admin.app is not None
    print(app.config.get("NOREPLY_EMAIL_SENDER"))

@pytest.mark.skip(reason="not print.")
def test_prints(app):
    print_blueprints(app)
    print_routes(app)
