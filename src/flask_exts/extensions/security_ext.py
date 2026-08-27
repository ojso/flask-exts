from ..extension.base import Extension
from ..security.core import Security

class SecurityExtension(Extension):
    @property
    def name(self) -> str:
        return "security"

    @property
    def priority(self) -> int:
        return 30

    @property
    def dependencies(self) -> list[str]:
        return ["usercenter"]

    def init_app(self, app):
        self._security = Security()
        self._security.init_app(app)
