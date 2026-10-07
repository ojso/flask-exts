from ..extension_core.base import Extension
from ..usercenter.core import UserCenter
from ..usercenter.user_view import UserView


class UserCenterExtension(Extension):
    @property
    def name(self) -> str:
        return "usercenter"

    @property
    def dependencies(self) -> list[str]:
        return ["admin"]

    def init_app(self, app):
        self._usercenter = UserCenter()
        self._usercenter.init_app(app)
        self.register_views(app)

    def register_views(self, app):
        admin = app.extensions["exts"].get_extension("admin").get_admin()
        admin.register_view(UserView(), is_menu=False)
