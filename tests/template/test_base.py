from flask_exts.proxies import _template


class TestBase:
    def test_theme(self, app):
        template = app.extensions["exts"].template
        theme = template.theme
        plugin_manager = theme.plugin_manager
        assert plugin_manager is not None
        # print("init plugins:", [k for k in plugin_manager.plugins])
        # print("init plugins:", [k for k in plugin_manager.enabled_plugins])
        assert len(plugin_manager.enabled_plugins) == 0
        assert len(plugin_manager.plugins) >= 9
        for p in ['bootstrap4', 'bootstrap5', 'clipboard', 'copybutton', 'detail_filter', 'jquery', 'model_action', 'qrcode', 'rediscli', 'sphinx_copybutton']:
            assert p in plugin_manager.plugins

    def test_default(self, app):
        with app.test_request_context():
            _template.theme.plugin_manager.enable_plugin(['jquery', 'bootstrap4'])
            # print(_template.theme.plugin_manager.plugins)
            # print(_template.theme.plugin_manager.enabled_plugins)
            css = _template.theme.plugin_manager.load_css()
            # print(css)
            assert "bootstrap.min.css" in str(css)
            js = _template.theme.plugin_manager.load_js()
            # print(js)
            assert "jquery.min.js" in str(js)
            assert "bootstrap.bundle.min.js" in str(js)
