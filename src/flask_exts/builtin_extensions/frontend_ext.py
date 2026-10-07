from flask import Blueprint

from ..extension_core.base import Extension
from ..forms.form.csrf import get_csrf_token
from ..frontend.template import Template


class FrontendExtension(Extension):
    @property
    def name(self) -> str:
        return "frontend"

    @property
    def dependencies(self) -> list[str]:
        return ["babel"]

    def init_app(self, app):
        self.app = app

        # blueprint _template
        self.init_template_blueprint(app)

        template = Template()
        self._template = template
        template.init_app(app)

        # set jinja
        app.jinja_env.globals["_template"] = template
        app.jinja_env.globals["csrf_token"] = get_csrf_token
        app.jinja_env.add_extension("jinja2.ext.do")
        # app.jinja_env.add_extension('jinja2.ext.debug')
        # template.plugin_manager.enable_plugin(["bootstrap5"])

    def init_template_blueprint(self, app):
        blueprint = Blueprint(
            "_template",
            __name__,
            url_prefix="/template",
            template_folder="../templates",
            static_folder="../static",
        )
        app.register_blueprint(blueprint)

    def get_template(self):
        return self._template
