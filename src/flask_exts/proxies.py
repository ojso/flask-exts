import typing as t

from flask import current_app
from werkzeug.local import LocalProxy

if t.TYPE_CHECKING:
    from .manager import Manager
    from .usercenter.base import UserCenter
    from .security.core import Security
    from .security.authorizer.base import Authorizer


_manager: "Manager" = LocalProxy(lambda: current_app.extensions["manager"])

_theme = LocalProxy(lambda: _manager.theme)

_usercenter: "UserCenter" = LocalProxy(lambda: _manager.usercenter)

_security: "Security" = LocalProxy(lambda: _manager.security)

_authorizer: "Authorizer" = LocalProxy(lambda: _manager.security.authorizer)

_admin = LocalProxy(lambda: _manager.admins[0])
