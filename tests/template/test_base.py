from flask_exts.proxies import _template
from flask import g

class TestBase:
    def test_base(self, app):
        template = app.extensions["exts"].template
        # theme
        theme = template.theme
        assert theme is not None
        # funcs
        funcs = template.funcs
        assert funcs is not None
        # plugins
        plugin_manager = template.plugin_manager
        assert plugin_manager is not None
        # print("init plugins:", [k for k in plugin_manager.plugins])
        # print("init plugins:", [k for k in plugin_manager.enabled_plugins])
        assert len(plugin_manager.enabled_plugins) == 0
        assert len(plugin_manager.plugins) >= 9
        for p in ['bootstrap4', 'bootstrap5', 'clipboard', 'copybutton', 'detail_filter', 'jquery', 'model_action', 'qrcode', 'rediscli', 'sphinx_copybutton']:
            assert p in plugin_manager.plugins

    def test_theme(self, app):
        with app.test_request_context():
            theme = _template.theme
            assert theme.icon_size == "1em"

    def test_funcs(self, app):
        with app.test_request_context():
            funcs = _template.funcs
            csrf_token = funcs.csrf_token()
            # print("csrf_token:", csrf_token)
            assert csrf_token is not None
            assert csrf_token == g.get("csrf_token")

            
    def test_plugins(self, app):
        with app.test_request_context():
            _template.plugin_manager.enable_plugin(['jquery', 'bootstrap4'])
            # print(_template.plugin_manager.plugins)
            # print(_template.plugin_manager.enabled_plugins)
            css = _template.plugin_manager.load_css()
            # print(css)
            assert "bootstrap.min.css" in str(css)
            js = _template.plugin_manager.load_js()
            # print(js)
            assert "jquery.min.js" in str(js)
            assert "bootstrap.bundle.min.js" in str(js)
