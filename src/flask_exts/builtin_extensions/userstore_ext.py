from ..extension_core.base import Extension
from ..userstore.sqla.userstore import SqlaUserStore


class UserStoreExtension(Extension):
    @property
    def name(self) -> str:
        return "userstore"

    @property
    def dependencies(self) -> list[str]:
        return ["database"]

    def init_app(self, app):
        self._userstore = SqlaUserStore()

    def get_userstore(self):
        return self._userstore
