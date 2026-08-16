from ..extension import Extension


class TemplateExtension(Extension):
    @property
    def name(self) -> str:
        return "template"

    @property
    def priority(self) -> int:
        return 30

    @property
    def dependencies(self) -> list[str]:
        return ["babel","database", "usercenter", "security"]

    def init_app(self, app):
        from ..template.core import Template

        self._template = Template()
        self._template.init_app(app)
