from typing import TYPE_CHECKING
from flask import current_app
from werkzeug.local import LocalProxy

if TYPE_CHECKING:
    from .exts import Exts
    from .template.core import Template
    from .usercenter.core import UserCenter
    from .usercenter.base_user_store import BaseUserStore
    from .security.core import Security
    from .admin.admin import Admin


current_exts: "Exts" = LocalProxy(lambda: current_app.extensions["exts"])

current_template: "Template" = LocalProxy(lambda: current_exts.get_extension("template")._template)

current_usercenter: "UserCenter" = LocalProxy(lambda: current_exts.get_extension("usercenter")._usercenter)

current_userstore: "BaseUserStore" = LocalProxy(lambda: current_usercenter.userstore)

current_security: "Security" = LocalProxy(lambda: current_exts.get_extension("security")._security)

current_admin: "Admin" = LocalProxy(lambda: current_exts.get_extension("admin")._admin)
