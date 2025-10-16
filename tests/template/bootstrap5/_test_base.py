from flask_exts.proxies import _template


class TestBase:
    def test_theme(self, app):
        with app.test_request_context():
            theme = _template.theme
            # print(theme)
            assert theme.bootstrap.version == 5
            css = theme.load_css()
            # print(css)
            assert "bootstrap.min.css" in css
            js = theme.load_js()
            # print(js)
            assert "jquery.slim.min.js" not in js
            assert "bootstrap.bundle.min.js" in js
