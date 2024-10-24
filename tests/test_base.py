from .funcs import print_blueprints
from .funcs import print_routes


def test_extensions(app):
    # print(app.extensions.keys())
    # print(app.extensions)
    assert "babel" in app.extensions
    assert "template" in app.extensions


def test_prints(app):
    # print_blueprints(app)
    # print_routes(app)
    pass
