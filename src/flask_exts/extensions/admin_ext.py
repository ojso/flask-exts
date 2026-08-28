from ..extension.base import Extension
from ..admin import Admin


class AdminExtension(Extension):
    @property
    def name(self) -> str:
        return "admin"

    @property
    def priority(self) -> int:
        return 50

    def init_app(self, app):
        self._admin = Admin()
        self._admin.init_app(app)

    def get_admin(self):
        return self._admin
