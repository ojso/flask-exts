import typing as t

from flask import current_app
from werkzeug.local import LocalProxy

if t.TYPE_CHECKING:
    from .exts import Exts
    from .template.base import Template
    from .usercenter.base_user_store import BaseUserStore
    from .security.core import Security


_exts: "Exts" = LocalProxy(lambda: current_app.extensions["exts"])

_template: "Template" = LocalProxy(lambda: _exts.template)

_userstore: "BaseUserStore" = LocalProxy(lambda: _exts.usercenter.userstore)

_security: "Security" = LocalProxy(lambda: _exts.security)
