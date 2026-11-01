from flask_exts.proxies import current_exts


class TestBase:
    def test_base(self, app):
        template = app.extensions["exts"].get_extension("frontend").get_template()
        plugin_manager = template.plugin_manager
        assert plugin_manager is not None
        assert len(plugin_manager._registry) >= 0

    def test_plugin_editable(self, app):
        with app.test_request_context():
            plugin_manager = (
                current_exts.get_extension("frontend").get_template().plugin_manager
            )
            plugin_manager.add_request_plugins(["editable"])
            ordered_names = plugin_manager.ordered_names()
            assert ["bootstrap5", "editable"] == ordered_names
            css = plugin_manager.load_styles()
            assert "bootstrap.min.css" in str(css)
            js = plugin_manager.load_scripts()
            assert "bootstrap.bundle.min.js" in str(js)
            assert "editable.js" in str(js)
