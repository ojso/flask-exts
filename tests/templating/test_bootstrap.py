from flask import current_app


class TestBootstrap:
    def test_load_css(self, app):
        with app.test_request_context():
            templating = current_app.extensions["templating"]
            # print(templating.bootstrap_version)
            css = templating.load_css()
            # print(css)
            assert "bootstrap.min.css" in css

    def test_load_js(self, app):
        with app.test_request_context():
            templating = current_app.extensions["templating"]
            js = templating.load_js()
            # print(js)
            assert "bootstrap" in js
