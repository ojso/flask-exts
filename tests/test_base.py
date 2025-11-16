import pytest
from .helper import print_blueprints
from .helper import print_routes


def test_extensions(app):
    # print(app.extensions)
    # print(app.extensions.keys())
    assert "babel" in app.extensions
    assert "sqlalchemy" in app.extensions
    assert getattr(app, "login_manager", None) is not None
    assert "exts" in app.extensions
    assert len(app.blueprints) == 3
    assert "_template" in app.blueprints
    assert "index" in app.blueprints
    assert "user" in app.blueprints
    assert "_template" in app.jinja_env.globals    
    exts = app.extensions["exts"]
    assert exts.usercenter is not None
    assert exts.security is not None
    assert exts.admin is not None
    admin = exts.admin
    assert admin.app is not None
    print(app.config.get("NOREPLY_EMAIL_SENDER"))

@pytest.mark.skip(reason="not print.")
def test_prints(app):
    print_blueprints(app)
    print_routes(app)
