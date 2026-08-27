from ..extension.base import Extension


class AdminExtension(Extension):
    @property
    def name(self) -> str:
        return "admin"

    @property
    def priority(self) -> int:
        return 40

    def init_app(self, app):
        from ..admin.admin import Admin

        self._admin = Admin()
        self._admin.init_app(app)
