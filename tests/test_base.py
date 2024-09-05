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

    def test_list_templates(self, app):
        # print("\n===== app.jinja_env.list_templates =====")
        for k in app.jinja_env.list_templates():
            # print(k)
            pass
