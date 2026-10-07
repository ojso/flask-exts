from ..admin import Admin
from ..extension_core.base import Extension


class AdminExtension(Extension):
    @property
    def name(self) -> str:
        return "admin"

    def init_app(self, app):
        self._admin = Admin()
        self._admin.init_app(app)

    def get_admin(self):
        return self._admin
