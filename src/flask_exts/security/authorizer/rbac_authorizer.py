"""Role and permission based access control modelled on Flask-RPBAC.

The requirement objects follow Flask-RPBAC's semantics:

- :class:`Role` and :class:`Permission` check values loaded for the user,
  with ``match="any"`` / ``match="all"`` (``Role`` defaults to any, ``Permission``
  to all, as in Flask-RPBAC).
- :class:`Predicate` wraps a user callable that receives a
  :class:`BuildContext` for request- and object-level checks.
- :class:`All`, :class:`Any` and :class:`Not` compose requirements, and
  ``&`` / ``|`` are shorthand for :class:`All` / :class:`Any`.

Unlike Flask-RPBAC, rules are declared on the view class instead of route
decorators, because this authorizer plugs into the existing
``Admin.allow`` -> ``Security.authorize_allow`` hook:

.. code-block:: python

    from flask_exts.security.authorizer.rbac_authorizer import (
        All,
        Permission,
        Predicate,
        Role,
    )


    def owns_ticket(ctx):
        view = ctx.view
        return view.ticket_owner_id == ctx.user.id


    class TicketView(ModelView):
        permission = All(Role("editor"), Predicate(owns_ticket))
        permissions = {"delete_view": Permission("ticket:delete")}
        roles = ("admin",)

Enable it with ``app.config["SECURITY_AUTHORIZER"] = "rbac"``. Roles and
permissions come from Flask-Login's ``current_user`` through optional loaders;
without loaders the authorizer reads ``user.get_roles()`` and
``user.get_permissions()`` when those methods exist.
"""

import typing as t
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field

from flask_login import current_user

from .base import Authorizer

__all__ = [
    "All",
    "Any",
    "Authenticated",
    "BuildContext",
    "Not",
    "Permission",
    "Predicate",
    "RBACAuthorizer",
    "Requirements",
    "Role",
    "contains_predicate",
]

_MATCH_MODES = frozenset({"any", "all"})


@dataclass
class BuildContext:
    """Request-scoped data handed to every requirement.

    Mirrors Flask-RPBAC's ``RPBACBuildContext``: ``kwargs`` carries the view
    function's keyword arguments, and ``pstore`` lets predicates share
    intermediate results within a single check.

    Attributes:
        user: The user the check applies to.
        roles: Role names loaded for that user.
        permissions: Permission names loaded for that user.
        kwargs: Keyword arguments of the protected view function.
        view: The admin view instance, when the check comes from a view.
        fn: The view function being called, when known.
        pstore: Scratch space shared by predicates in one check.
    """

    user: t.Any = None
    roles: set[str] = field(default_factory=set)
    permissions: set[str] = field(default_factory=set)
    kwargs: dict[str, t.Any] = field(default_factory=dict)
    view: t.Any = None
    fn: t.Any = None
    object: t.Any = None
    objects: tuple[t.Any, ...] = ()
    pstore: dict[str, t.Any] = field(default_factory=dict)


class Requirements(ABC):
    """Base class for composable requirements.

    Subclasses implement :meth:`check`. ``&`` and ``|`` return :class:`All` and
    :class:`Any`, matching Flask-RPBAC's operator behaviour.
    """

    @abstractmethod
    def check(self, ctx: BuildContext) -> bool:
        """Return whether the requirement is satisfied.

        Args:
            ctx: The request-scoped build context.

        Returns:
            bool: ``True`` when the requirement passes.
        """

    def escalate(self, rpbac: t.Any) -> None:
        """Hook for loading data on demand; kept for Flask-RPBAC parity.

        This authorizer loads roles and permissions before the check runs, so
        there is nothing left to escalate.
        """

    def __and__(self, other: "Requirements") -> "Requirements":
        return All(self, other)

    def __or__(self, other: "Requirements") -> "Requirements":
        return Any(self, other)


class Role(Requirements):
    """Requirement that checks the roles loaded for the user."""

    def __init__(self, *roles: str, match: str = "any"):
        """Initialize the requirement.

        Args:
            *roles: Role names to look for.
            match: ``"any"`` (default) when one role is enough, ``"all"`` when
                every role is required.

        Raises:
            ValueError: If no role is given or ``match`` is unknown. An empty
                requirement would silently deny every request.
        """
        if not roles:
            raise ValueError("Role requires at least one role name.")
        if match not in _MATCH_MODES:
            raise ValueError(f"match must be 'any' or 'all', got {match!r}.")
        self.roles = tuple(roles)
        self.match = match

    def check(self, ctx: BuildContext) -> bool:
        if self.match == "all":
            return all(role in ctx.roles for role in self.roles)
        return any(role in ctx.roles for role in self.roles)


class Permission(Requirements):
    """Requirement that checks the permission names loaded for the user."""

    def __init__(self, *permissions: str, match: str = "all"):
        """Initialize the requirement.

        Args:
            *permissions: Permission names such as ``"post:write"``.
            match: ``"all"`` (default) when every permission is required,
                ``"any"`` when one is enough.

        Raises:
            ValueError: If no permission is given or ``match`` is unknown.
        """
        if not permissions:
            raise ValueError("Permission requires at least one permission name.")
        if match not in _MATCH_MODES:
            raise ValueError(f"match must be 'any' or 'all', got {match!r}.")
        self.permissions = tuple(permissions)
        self.match = match

    def check(self, ctx: BuildContext) -> bool:
        if self.match == "any":
            return any(item in ctx.permissions for item in self.permissions)
        return all(item in ctx.permissions for item in self.permissions)


class Predicate(Requirements):
    """Requirement backed by a user callable.

    The callable receives a :class:`BuildContext` and returns a truthy value.
    Use it when access depends on the object named by the request rather than
    on user-wide roles or permissions.
    """

    def __init__(self, func: Callable[[BuildContext], t.Any]):
        """Initialize the requirement.

        Args:
            func: Callable taking the context and returning a truthy value.

        Raises:
            TypeError: If ``func`` is not callable.
        """
        if not callable(func):
            raise TypeError("Predicate requires a callable taking the context.")
        self.func = func

    def check(self, ctx: BuildContext) -> bool:
        return bool(self.func(ctx))


class All(Requirements):
    """Requirement that passes only when every child requirement passes."""

    def __init__(self, *requirements: Requirements):
        self.requirements = tuple(requirements)

    def check(self, ctx: BuildContext) -> bool:
        return all(item.check(ctx) for item in self.requirements)


class Any(Requirements):
    """Requirement that passes when at least one child requirement passes."""

    def __init__(self, *requirements: Requirements):
        self.requirements = tuple(requirements)

    def check(self, ctx: BuildContext) -> bool:
        return any(item.check(ctx) for item in self.requirements)


class Not(Requirements):
    """Requirement that passes when none of its children pass."""

    def __init__(self, *requirements: Requirements):
        self.requirements = tuple(requirements)

    def check(self, ctx: BuildContext) -> bool:
        return not any(item.check(ctx) for item in self.requirements)


class Authenticated(Requirements):
    """Requirement satisfied by any authenticated user."""

    def check(self, ctx: BuildContext) -> bool:
        return bool(getattr(ctx.user, "is_authenticated", False))


def _as_requirement(value: t.Any) -> Requirements | None:
    """Coerce a declared view attribute into a requirement.

    Args:
        value: A requirement instance, a role name, or ``None``.

    Returns:
        Requirements | None: The requirement, or ``None`` when nothing was
            declared.

    Raises:
        TypeError: If the value is not a supported declaration.
    """
    if value is None:
        return None
    if isinstance(value, Requirements):
        return value
    if isinstance(value, str):
        return Role(value)
    raise TypeError(
        f"Unsupported permission declaration {value!r};"
        " use Role, Permission, Predicate, All, Any or Not."
    )


def contains_predicate(requirement: t.Any) -> bool:
    """Return whether a requirement declaration contains a ``Predicate``.

    Composite requirements are searched recursively so a view that declares
    ``All(Role(...), Predicate(...))`` still counts as object-level.

    Args:
        requirement: Requirement declaration or ``None``.

    Returns:
        bool: ``True`` when a ``Predicate`` appears anywhere in the tree.
    """
    if isinstance(requirement, Predicate):
        return True
    return any(
        contains_predicate(item) for item in getattr(requirement, "requirements", ())
    )


class RBACAuthorizer(Authorizer):
    """Requirement-first authorizer with the existing role rule as fallback."""

    def __init__(self, app=None):
        self.app = None
        if app is not None:
            self.init_app(app)
        self._role_loader: Callable[[], Iterable[str]] | None = None
        self._permission_loader: Callable[[], Iterable[str]] | None = None
        self._user_data_loader: Callable[[], Mapping[str, Iterable[str]]] | None = None

    def init_app(self, app):
        """Bind the authorizer to an application."""
        self.app = app

    def role_loader(self, func: Callable[[], Iterable[str]]) -> Callable:
        """Register the callable returning the current user's role names."""
        self._role_loader = func
        return func

    def permission_loader(self, func: Callable[[], Iterable[str]]) -> Callable:
        """Register the callable returning the current user's permission names."""
        self._permission_loader = func
        return func

    def user_data_loader(
        self, func: Callable[[], Mapping[str, Iterable[str]]]
    ) -> Callable:
        """Register one callable returning both roles and permissions.

        The callable must return a mapping such as
        ``{"roles": [...], "permissions": [...]}``. When set, it takes
        precedence over the two individual loaders.
        """
        self._user_data_loader = func
        return func

    def build_context(
        self,
        user: t.Any,
        view: t.Any = None,
        fn: t.Any = None,
        obj: t.Any = None,
        objects: Iterable[t.Any] = (),
        **kwargs: t.Any,
    ) -> BuildContext:
        """Return a build context for ``user``.

        Args:
            user: The user the check applies to.
            view: The admin view instance, when applicable.
            fn: The view function being called, when known.
            obj: The single object currently being checked, when applicable.
            objects: The full batch of objects for the current request.
            **kwargs: Extra request data exposed to predicates.

        Returns:
            BuildContext: Context with roles and permissions already loaded.
        """
        if self._user_data_loader is not None:
            data = self._user_data_loader() or {}
            roles = self._as_names(data.get("roles"))
            permissions = self._as_names(data.get("permissions"))
        else:
            roles = self._load(self._role_loader, user, "get_roles")
            permissions = self._load(self._permission_loader, user, "get_permissions")
        return BuildContext(
            user=user,
            roles=roles,
            permissions=permissions,
            kwargs=dict(kwargs),
            view=view,
            fn=fn,
            object=obj,
            objects=tuple(objects),
        )

    def can(self, *requirements: Requirements, **kwargs: t.Any) -> bool:
        """Return whether the current (or given) user meets every requirement.

        Args:
            *requirements: Requirements to evaluate.
            **kwargs: ``user``, ``view``, ``fn`` and extra request data.

        Returns:
            bool: ``True`` when all requirements pass.
        """
        user = kwargs.pop("user", None)
        ctx = self.build_context(
            user, view=kwargs.pop("view", None), fn=kwargs.pop("fn", None), **kwargs
        )
        return all(item.check(ctx) for item in requirements)

    def has_role(self, role: str, user: t.Any = None) -> bool:
        """Return whether ``user`` (default: current user) holds ``role``."""
        return role in self.build_context(user).roles

    def has_permission(self, permission: str, user: t.Any = None) -> bool:
        """Return whether ``user`` (default: current user) has ``permission``."""
        return permission in self.build_context(user).permissions

    def allow(self, *args: t.Any, **kwargs: t.Any) -> bool:
        user = kwargs.get("user")
        view = kwargs.get("view")

        decision = self.check_view_access(user, view, kwargs.get("fn"))
        if decision is not None:
            return decision

        if not getattr(user, "is_active", True):
            return False

        requirement = self.resolve_requirement(view, kwargs.get("fn"))
        if requirement is None:
            return self.allow_by_roles(**{**kwargs, "user": user})

        ctx = self.build_context(
            user, view=view, fn=kwargs.get("fn"), **self._extra(kwargs)
        )
        return requirement.check(ctx)

    def authorize_object(self, view, fn, obj, requirement, user=None):
        """Authorize ``obj`` for the exposed method ``fn``.

        The shared login/superuser gate runs first so the existing ``admin``
        and public-view rules keep working. Otherwise the requirement is
        evaluated with ``ctx.object`` set to ``obj``.

        Args:
            view: The admin view instance owning the object.
            fn: The exposed view method being called.
            obj: The object the request resolved to.
            requirement: Object-level requirement to evaluate.
            user: User to check; defaults to the current user.

        Returns:
            bool: ``True`` when the object is allowed.
        """
        if user is None:
            user = current_user

        decision = self.check_view_access(user, view, fn)
        if decision is not None:
            return decision

        ctx = self.build_context(user, view=view, fn=fn, obj=obj)
        return requirement.check(ctx)

    def resolve_requirement(self, view: t.Any, fn: t.Any = None) -> Requirements | None:
        """Return the requirement declared for ``view`` and ``fn``.

        Args:
            view: The admin view instance, when the check comes from a view.
            fn: The view function being called, when known.

        Returns:
            Requirements | None: The first declared requirement, or ``None``
                when the view declares nothing and the role fallback should run.

        Raises:
            TypeError: If a declared attribute is not a supported type.
        """
        if view is None:
            return None

        per_function = getattr(view, "permissions", None)
        if fn is not None and isinstance(per_function, Mapping):
            declared = per_function.get(getattr(fn, "__name__", None))
            requirement = _as_requirement(declared)
            if requirement is not None:
                return requirement

        requirement = _as_requirement(getattr(view, "permission", None))
        if requirement is not None:
            return requirement

        roles = getattr(view, "roles", None)
        if roles:
            names = (roles,) if isinstance(roles, str) else tuple(roles)
            return Role(*names)
        return None

    @staticmethod
    def _as_names(values: t.Any) -> set[str]:
        return {str(item) for item in (values or ())}

    @classmethod
    def _load(
        cls,
        loader: Callable[[], Iterable[str]] | None,
        user: t.Any,
        getter_name: str,
    ) -> set[str]:
        if loader is not None:
            return cls._as_names(loader())
        getter = getattr(user, getter_name, None)
        if callable(getter):
            return cls._as_names(getter())
        return set()

    @staticmethod
    def _extra(kwargs: Mapping[str, t.Any]) -> dict[str, t.Any]:
        """Return request data without the keys consumed by the authorizer."""
        return {
            key: value
            for key, value in kwargs.items()
            if key not in {"user", "view", "fn"}
        }
