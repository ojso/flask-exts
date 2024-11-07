from .funcs import print_blueprints
from .funcs import print_routes


def test_extensions(app):
    # print(app.extensions)
    # print(app.extensions.keys())
    assert "babel" in app.extensions
    assert "template" in app.extensions
    assert getattr(app, "login_manager", None) is not None


def _test_prints(app):
    # print_blueprints(app)
    # print_routes(app)
    pass
