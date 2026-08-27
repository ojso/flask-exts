from typing import TYPE_CHECKING
from flask import current_app
from werkzeug.local import LocalProxy

if TYPE_CHECKING:
    from .extension.manager import ExtensionManager
    from .usercenter.core import UserCenter
    from .usercenter.user_store import UserStore
    from .security.core import Security
    from .admin.admin import Admin


current_exts: "ExtensionManager" = LocalProxy(lambda: current_app.extensions["exts"])

current_userstore: "UserStore" = LocalProxy(
    lambda: current_exts.get_extension("userstore").get_store()
)

current_security: "Security" = LocalProxy(
    lambda: current_exts.get_extension("security")._security
)

current_admin: "Admin" = LocalProxy(lambda: current_exts.get_extension("admin")._admin)
