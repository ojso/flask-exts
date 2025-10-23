from flask_exts.proxies import _template


class TestBase:
    def test_default(self, app):
        with app.test_request_context():
            _template.theme.plugin.enable_plugin(['jquery', 'bootstrap4'])
            # print(_template.theme.plugin.registered_plugins)
            # print(_template.theme.plugin.enabled_plugins)
            css = _template.theme.plugin.load_css()
            # print(css)
            assert "bootstrap.min.css" in str(css)
            js = _template.theme.plugin.load_js()
            # print(js)
            assert "jquery.min.js" in str(js)
            assert "bootstrap.bundle.min.js" in str(js)
