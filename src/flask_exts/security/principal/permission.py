from typing import Optional, Union, Set, Dict
from functools import partial
from collections import namedtuple
from flask import g
from .identity import Identity
from .identity_context import IdentityContext

Need = namedtuple("Need", ["method", "value"])
"""A required need

This is just a named tuple, and practically any tuple will do.

The ``method`` attribute can be used to look up element 0, and the ``value``
attribute can be used to look up element 1.
"""


UserNeed = partial(Need, "id")
UserNeed.__doc__ = """A need with the method preset to `"id"`."""


RoleNeed = partial(Need, "role")
RoleNeed.__doc__ = """A need with the method preset to `"role"`."""


TypeNeed = partial(Need, "type")
TypeNeed.__doc__ = """A need with the method preset to `"type"`."""


ActionNeed = partial(Need, "action")
ActionNeed.__doc__ = """A need with the method preset to `"action"`."""


ItemNeed = namedtuple("ItemNeed", ["method", "value", "type"])
"""A required item need

An item need is just a named tuple, and practically any tuple will do. In
addition to other Needs, there is a type, for example this could be specified
as::

    ItemNeed('update', 27, 'posts')
    ('update', 27, 'posts') # or like this

And that might describe the permission to update a particular blog post. In
reality, the developer is free to choose whatever convention the permissions
are.
"""


class BasePermission:
    """The Base Permission."""

    http_exception = None

    def _bool(self) -> bool:
        return bool(self.can())

    def __nonzero__(self) -> bool:
        """Equivalent to ``self.can()``."""
        return self._bool()

    def __bool__(self) -> bool:
        """Equivalent to ``self.can()``."""
        return self._bool()

    def __or__(self, other: "BasePermission") -> "BasePermission":
        """See ``OrPermission``."""
        return self.or_(other)

    def or_(self, other: "BasePermission") -> "BasePermission":
        return OrPermission(self, other)

    def __and__(self, other: "BasePermission") -> "BasePermission":
        """See ``AndPermission``."""
        return self.and_(other)

    def and_(self, other: "BasePermission") -> "BasePermission":
        return AndPermission(self, other)

    def __invert__(self) -> Union["NotPermission", "BasePermission"]:
        """See ``NotPermission``."""
        return self.invert()

    def invert(self) -> Union["NotPermission", "BasePermission"]:
        return NotPermission(self)

    def require(self, http_exception: Optional[int] = None) -> "IdentityContext":
        """Create a principal for this permission.

        The principal may be used as a context manager, or a decroator.

        If ``http_exception`` is passed then ``abort()`` will be called
        with the HTTP exception code. Otherwise a ``PermissionDenied``
        exception will be raised if the identity does not meet the
        requirements.

        :param http_exception: the HTTP exception code (403, 401 etc)
        """

        if http_exception is None:
            http_exception = self.http_exception

        return IdentityContext(self, http_exception)

    def test(self, http_exception: Optional[int] = None) -> None:
        """
        Checks if permission available and raises relevant exception
        if not. This is useful if you just want to check permission
        without wrapping everything in a require() block.

        This is equivalent to::

            with permission.require():
                pass
        """

        with self.require(http_exception):
            pass

    def allows(self, identity: "Identity") -> bool:
        """Whether the identity can access this permission.

        :param identity: The identity
        """

        raise NotImplementedError

    def can(self) -> bool:
        """Whether the required context for this permission has access

        This creates an identity context and tests whether it can access this
        permission
        """
        return self.require().can()


class _NaryOperatorPermission(BasePermission):

    def __init__(self, *permissions: BasePermission) -> None:
        self.permissions: Set[BasePermission] = set(permissions)


class OrPermission(_NaryOperatorPermission):
    """Result of bitwise ``or`` of BasePermission"""

    def allows(self, identity: Identity) -> bool:
        """
        Checks for any of the nested permission instances that allow the
        identity and return True, else return False.

        :param identity: The identity.
        """

        return any(p.allows(identity) for p in self.permissions)


class AndPermission(_NaryOperatorPermission):
    """Result of bitwise ``and`` of BasePermission"""

    def allows(self, identity: Identity) -> bool:
        """
        Checks for any of the nested permission instances that disallow
        the identity and return False, else return True.

        :param identity: The identity.
        """

        return all(p.allows(identity) for p in self.permissions)


class NotPermission(BasePermission):
    """
    Result of bitwise ``not`` of BasePermission

    Really could be implemented by returning a transformed result of the
    source class of itself, but for the sake of clear presentation I am
    not doing that.
    """

    def __init__(self, permission: BasePermission) -> None:
        self.permission = permission

    def invert(self) -> BasePermission:
        return self.permission

    def allows(self, identity: Identity) -> bool:
        return not self.permission.allows(identity)


class Permission(BasePermission):
    """Represents needs, any of which must be present to access a resource

    :param needs: The needs for this permission
    """

    def __init__(self, *needs: Union[Need, ItemNeed]) -> None:
        """A set of needs, any of which must be present in an identity to have access."""

        self.perms: Dict[Union[Need, ItemNeed], bool] = {n: True for n in needs}

    def __or__(
        self, other: Union["Permission", BasePermission]
    ) -> Union["Permission", BasePermission]:
        """Does the same thing as ``self.union(other)``"""
        if isinstance(other, Permission):
            return self.union(other)
        return super().__or__(other)

    def __sub__(self, other: "Permission") -> "Permission":
        """Does the same thing as ``self.difference(other)``"""
        return self.difference(other)

    def __contains__(self, other: "Permission") -> bool:
        """Does the same thing as ``other.issubset(self)``."""
        return other.issubset(self)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} needs={self.needs} excludes={self.excludes}>"
        )

    @property
    def needs(self) -> Set[Union[Need, ItemNeed]]:
        return {n for n, v in self.perms.items() if v}

    @property
    def excludes(self) -> Set[Union[Need, ItemNeed]]:
        return {n for n, v in self.perms.items() if not v}

    def reverse(self) -> "Permission":
        """
        Returns reverse of current state (needs->excludes, excludes->needs)
        """

        p = Permission()
        # flipping the values determining whether or not the key
        # is a need or exclude
        p.perms.update({n: not v for n, v in self.perms.items()})
        return p

    def union(self, other: "Permission") -> "Permission":
        """Create a new permission with the requirements of the union of this
        and other.

        :param other: The other permission
        """
        p = Permission()
        p.perms = {
            **{n: True for n in self.needs.union(other.needs)},
            **{e: False for e in self.excludes.union(other.excludes)},
        }
        return p

    def difference(self, other: "Permission") -> "Permission":
        """Create a new permission consisting of requirements in this
        permission and not in the other.
        """

        p = Permission()
        # diff-ing needs and excludes from both Permissions
        p.perms = {
            **{n: True for n in self.needs.difference(other.needs)},
            **{e: False for e in self.excludes.difference(other.excludes)},
        }
        return p

    def issubset(self, other: "Permission") -> bool:
        """Whether this permission needs are a subset of another

        :param other: The other permission
        """
        return self.needs.issubset(other.needs) and self.excludes.issubset(
            other.excludes
        )

    def allows(self, identity: Identity) -> bool:
        """Whether the identity can access this permission.

        :param identity: The identity
        """
        if self.needs and not self.needs.intersection(identity.provides):
            return False

        if self.excludes and self.excludes.intersection(identity.provides):
            return False

        return True


class Denial(Permission):
    """
    Shortcut class for passing excluded needs.
    """

    def __init__(self, *excludes: Union[Need, ItemNeed]) -> None:
        self.perms = {e: False for e in excludes}

