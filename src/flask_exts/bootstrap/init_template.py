def init_jinja(app):
    app.jinja_env.add_extension("jinja2.ext.do")


def init_plugins(app):
    app.extensions["exts"].template.plugin_manager.enable_plugin(["bootstrap5"])
