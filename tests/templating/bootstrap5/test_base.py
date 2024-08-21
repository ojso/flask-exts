from flask import current_app


class TestBase:
    def test_version(self, app):
        with app.test_request_context():
            templating = current_app.extensions["templating"]
            assert templating.bootstrap_version == 5

    def test_load_js(self, app):
        with app.test_request_context():
            templating = current_app.extensions["templating"]
            js = templating.load_js()
            # print(js)
            assert "jquery" not in js
            assert "bootstrap" in js
