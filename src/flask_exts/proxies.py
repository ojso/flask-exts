import typing as t

from flask import current_app
from werkzeug.local import LocalProxy

if t.TYPE_CHECKING:
    from .manager import Manager
    from .template.base import Template
    from .usercenter.base_user_store import BaseUserStore
    from .security.core import Security


_manager: "Manager" = LocalProxy(lambda: current_app.extensions["manager"])

_template: "Template" = LocalProxy(lambda: _manager.template)

_userstore: "BaseUserStore" = LocalProxy(lambda: _manager.usercenter.userstore)

_security: "Security" = LocalProxy(lambda: _manager.security)
