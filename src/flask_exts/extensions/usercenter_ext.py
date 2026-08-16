from ..extension import Extension


class UserCenterExtension(Extension):
    @property
    def name(self) -> str:
        return "usercenter"

    @property
    def priority(self) -> int:
        return 20

    @property
    def dependencies(self) -> list[str]:
        return ["database"]

    def init_app(self, app):
        from ..usercenter.core import UserCenter

        self._usercenter = UserCenter()
        self._usercenter.init_app(app)
