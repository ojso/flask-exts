from ..extension_core.base import Extension
from ..usercenter.core import UserCenter


class UserCenterExtension(Extension):
    @property
    def name(self) -> str:
        return "usercenter"

    @property
    def priority(self) -> int:
        return 30

    @property
    def dependencies(self) -> list[str]:
        return ["userstore"]

    def init_app(self, app):
        self._usercenter = UserCenter()
        self._usercenter.init_app(app)
