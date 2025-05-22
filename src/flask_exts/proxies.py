import typing as t

from flask import current_app
from werkzeug.local import LocalProxy

if t.TYPE_CHECKING:
    from .manager import Manager
    from .usercenter.base import BaseUserCenter
    from .security.core import Security
    from .authorize.base import BaseAuthorizer


_manager: "Manager" = LocalProxy(lambda: current_app.extensions["manager"])

current_theme = LocalProxy(lambda: _manager.theme)

current_usercenter: "BaseUserCenter" = LocalProxy(lambda: _manager.usercenter)

current_authorizer: "BaseAuthorizer" = LocalProxy(lambda: _manager.authorizer)

_security: "Security" = LocalProxy(lambda: _manager.security)

current_admin = LocalProxy(lambda: _manager.admins[0])
