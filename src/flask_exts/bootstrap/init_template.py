def enable_plugins(app):
    app.jinja_env.add_extension("jinja2.ext.do")
    # app.extensions["exts"].template.plugin_manager.enable_plugin(
    #     ["jquery", "bootstrap5"]
    # )
