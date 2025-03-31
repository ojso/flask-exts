import typing as t

from flask import current_app
from werkzeug.local import LocalProxy

if t.TYPE_CHECKING:
    from .core import Security

_security: "Security" = LocalProxy(lambda: current_app.extensions["security"])

current_usercenter = LocalProxy(lambda: _security.usercenter)

current_casbinenforcer = LocalProxy(lambda: _security.casbin.get_enforcer())
