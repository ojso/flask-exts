from .funcs import print_blueprints
from .funcs import print_routes


def test_extensions(app):
    # print(app.extensions)
    # print(app.extensions.keys())
    assert "babel" in app.extensions
    assert "sqlalchemy" in app.extensions
    assert getattr(app, "login_manager", None) is not None
    assert "manager" in app.extensions
    manager = app.extensions["manager"]
    assert manager.theme is not None
    assert manager.usercenter is not None
    assert manager.security is not None

def test_prints(app):
    print_blueprints(app)
    print_routes(app)
