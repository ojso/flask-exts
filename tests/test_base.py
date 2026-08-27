import pytest


def test_extensions(app):
    # print(app.extensions)
    # print(app.extensions.keys())
    assert "exts" in app.extensions
    assert "babel" in app.extensions
    assert "sqlalchemy" in app.extensions
