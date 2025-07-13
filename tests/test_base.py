from .utils import print_blueprints
from .utils import print_routes


def test_extensions(app):
    # print(app.extensions)
    # print(app.extensions.keys())
    assert "babel" in app.extensions
    assert "sqlalchemy" in app.extensions
    assert getattr(app, "login_manager", None) is not None
    assert "manager" in app.extensions
    assert "template" in app.jinja_env.globals
    manager = app.extensions["manager"]
    assert manager.usercenter is not None
    assert manager.security is not None

def test_prints(app):
    print_blueprints(app)
    print_routes(app)
