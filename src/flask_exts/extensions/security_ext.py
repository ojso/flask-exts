from ..extension import Extension


class SecurityExtension(Extension):
    @property
    def name(self) -> str:
        return "security"

    @property
    def priority(self) -> int:
        return 30

    @property
    def dependencies(self) -> list[str]:
        return ["database", "usercenter"]

    def init_app(self, app):
        from ..security.core import Security

        self._security = Security()
        self._security.init_app(app)
