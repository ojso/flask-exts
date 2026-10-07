from ..extension_core.base import Extension
from ..security.core import Security


class SecurityExtension(Extension):
    @property
    def name(self) -> str:
        return "security"

    def init_app(self, app):
        self._security = Security()
        self._security.init_app(app)

    def get_security(self):
        return self._security
