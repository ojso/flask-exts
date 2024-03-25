class TestBase:
    def test_extensions(self, app):
        manager = app.extensions.get("manager")
        assert manager is not None
        babel = app.extensions.get("babel")
        assert babel is not None
