from flask import current_app


class TestBase:
    def test_version(self, app):
        with app.test_request_context():
            templating = current_app.extensions["templating"]
            assert templating.bootstrap_version == 4

    def test_version(self, app):
        with app.test_request_context():
            templating = current_app.extensions["templating"]
            js = templating.load_js()
            assert "jquery" in js
            assert "bootstrap" in js
