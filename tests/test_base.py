class TestBase:
    def test_extensions(self, app):
        # print(app.extensions.keys())
        # print(app.extensions)
        assert "manager" in app.extensions
        assert "babel" in app.extensions
        assert "templating" in app.extensions

    def test_blueprints(self, app):
        # print(app.blueprints)
        pass
