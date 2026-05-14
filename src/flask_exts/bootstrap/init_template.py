def init_jinja(app):
    app.jinja_env.add_extension("jinja2.ext.do")
    # app.jinja_env.add_extension('jinja2.ext.debug')

def init_plugins(app):
    pass
    # app.extensions["exts"].template.plugin_manager.enable_plugin(["bootstrap5"])
