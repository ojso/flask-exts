from typing import TYPE_CHECKING
from flask import current_app
from werkzeug.local import LocalProxy

if TYPE_CHECKING:
    from .extension_core.manager import ExtensionManager
    from .userstore.store import UserStore
    from .security.core import Security
    from .web import Admin


current_exts: "ExtensionManager" = LocalProxy(lambda: current_app.extensions["exts"])

current_userstore: "UserStore" = LocalProxy(
    lambda: current_exts.get_extension("userstore").get_userstore()
)

current_security: "Security" = LocalProxy(
    lambda: current_exts.get_extension("security").get_security()
)

current_admin: "Admin" = LocalProxy(
    lambda: current_exts.get_extension("admin").get_admin()
)
