from flask_exts.proxies import current_exts
from flask import g

class TestBase:
    def test_base(self, app):
        template = app.extensions["exts"].get_extension("html")._template
        # theme
        theme = template.theme
        assert theme is not None
        # plugins
        plugin_manager = template.plugin_manager
        assert plugin_manager is not None
        assert len(plugin_manager._registry) >= 0


    def test_theme(self, app):
        template = app.extensions["exts"].get_extension("html")._template
        theme = template.theme
        assert theme.icon_size == "1em"
         
    def test_plugins(self, app):
        with app.test_request_context():
            plugin_manager = current_exts.get_extension("html")._template.plugin_manager
            plugin_manager.add_request_plugins(['jquery', 'bootstrap4'])
            css = plugin_manager.load_css()
            # print(css)
            assert "bootstrap.min.css" in str(css)
            js = plugin_manager.load_js()
            # print(js)
            assert "jquery.min.js" in str(js)
            assert "bootstrap.bundle.min.js" in str(js)
