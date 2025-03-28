import typing as t

from flask import current_app
from werkzeug.local import LocalProxy

if t.TYPE_CHECKING:
    from .core import Security

_security: "Security" = LocalProxy(lambda: current_app.extensions["security"])

_casbin = LocalProxy(lambda: current_app.extensions["security"].casbin)
