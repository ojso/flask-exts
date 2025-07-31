import typing as t

from flask import current_app
from werkzeug.local import LocalProxy

if t.TYPE_CHECKING:
    from .manager import Manager
    from .template.base import Template
    from .usercenter.base_usercenter import BaseUserCenter
    from .security.core import Security
    from .security.authorizer.base import Authorizer


_manager: "Manager" = LocalProxy(lambda: current_app.extensions["manager"])

_template: "Template" = LocalProxy(lambda: _manager.template)

_usercenter: "BaseUserCenter" = LocalProxy(lambda: _manager.usercenter)

_security: "Security" = LocalProxy(lambda: _manager.security)

_authorizer: "Authorizer" = LocalProxy(lambda: _manager.security.authorizer)
