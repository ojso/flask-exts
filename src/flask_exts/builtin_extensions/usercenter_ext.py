from ..extension_core.base import Extension
from ..usercenter.core import UserCenter
from ..usercenter.user_view import UserView


class UserCenterExtension(Extension):
    @property
    def name(self) -> str:
        return "usercenter"

    def init_app(self, app):
        self._usercenter = UserCenter()
        self._usercenter.init_app(app)

    def get_admin_views(self):
        return [(UserView(), False)]
