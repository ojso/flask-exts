from typing import Optional
from functools import wraps
from flask import g
from flask import abort
from .identity import Identity


class PermissionDenied(RuntimeError):
    """Permission denied to the resource"""


class IdentityContext:
    """The context of an identity for a permission.

    .. note:: This is usually created by the Permission.require method
              call for normal use-cases.

    The principal behaves as either a context manager or a decorator. The
    permission is checked for provision in the identity, and if available the
    flow is continued (context manager) or the function is executed (decorator).
    """

    def __init__(self, permission, http_exception: Optional[int] = None):
        self.permission = permission
        self.http_exception = http_exception

    @property
    def identity(self) -> "Identity":
        """The identity"""
        return g.identity

    def can(self) -> bool:
        """Whether the identity has access to the permission"""
        return self.permission.allows(self.identity)

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kw):
            with self:
                rv = f(*args, **kw)
            return rv

        return wrapper

    def __enter__(self) -> None:
        if not self.can():
            if self.http_exception:
                abort(self.http_exception, self.permission)
            raise PermissionDenied(self.permission)

    def __exit__(self, *args) -> None:
        pass
