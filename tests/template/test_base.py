from flask_exts.proxies import _template


class TestBase:
    def test_default(self, app):
        with app.test_request_context():
            css = _template.load_all_css()
            # print(css)
            assert "bootstrap.min.css" in css
            js = _template.load_all_js()
            # print(js)
            assert "jquery.min.js" in js
            assert "bootstrap.bundle.min.js" in js
