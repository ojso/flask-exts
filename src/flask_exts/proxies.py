import typing as t

from flask import current_app
from werkzeug.local import LocalProxy

if t.TYPE_CHECKING:
    from .security.core import Security
    from .security.usercenter import BaseUserCenter
    from .security.authorize.base import BaseAuthorizer

_security: "Security" = LocalProxy(lambda: current_app.extensions["security"])

current_usercenter: "BaseUserCenter" = LocalProxy(lambda: _security.usercenter)

current_authorizer: "BaseAuthorizer" = LocalProxy(lambda: _security.authorizer)

current_admin = LocalProxy(lambda: current_app.extensions["admin"][0])
