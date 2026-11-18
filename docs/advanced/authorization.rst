Authorization with requirements
===============================

Flask-Exts ships two authorizers:

- ``SimpleAuthorizer`` (default) decides access from the ``admin`` and
  ``role_need`` roles.
- ``RBACAuthorizer`` adds a Flask-RPBAC style requirement model so a view can
  require roles, permissions, object-level predicates, or any composition of
  them.

Select the RBAC authorizer with one config value::

    app.config["SECURITY_AUTHORIZER"] = "rbac"

``"simple"`` is the default. Any other value raises ``ValueError`` while the
security registry initializes; it never falls back silently.

Requirement model
-----------------

Requirements are small objects evaluated against a ``BuildContext``. The
context carries the user, the roles and permissions loaded for that user, the
view, the view function, the request keyword arguments, and a scratch
``pstore`` shared by predicates in one check.

Roles
~~~~~

``Role(*names, match="any")`` passes when one of the names is present by
default. Use ``match="all"`` when every name is required::

    from flask_exts.security.authorizer.rbac_authorizer import Role

    Role("admin")                         # any: admin is enough
    Role("admin", "editor", match="all")  # all: both are required

Permissions
~~~~~~~~~~~

``Permission(*names, match="all")`` is the mirror image: every permission is
required by default, and ``match="any"`` accepts one of them::

    from flask_exts.security.authorizer.rbac_authorizer import Permission

    Permission("ticket:read", "ticket:write")
    Permission("ticket:read", "ticket:write", match="any")

Permissions are loaded names; the ``admin`` superuser rule is applied earlier by
the shared view gate, not inside ``Permission``.

Predicates
~~~~~~~~~~

``Predicate(func)`` wraps a callable for object-level checks. The callable
receives the ``BuildContext`` and returns a truthy value::

    from flask_exts.security.authorizer.rbac_authorizer import Predicate


    def owns_ticket(ctx):
        return ctx.view.ticket_owner_id == ctx.user.id


    owns_ticket_requirement = Predicate(owns_ticket)

Composition
~~~~~~~~~~~

``All``, ``Any`` and ``Not`` compose requirements, and ``&`` / ``|`` are
shorthand for ``All`` / ``Any``::

    from flask_exts.security.authorizer.rbac_authorizer import (
        All,
        Any,
        Not,
        Permission,
        Role,
    )

    admin_writer = All(Role("admin"), Permission("ticket:write"))
    editor_or_admin = Role("editor") | Role("admin")
    not_suspended = Not(Role("suspended"))

``Authenticated()`` passes for any authenticated user. An empty ``Role()`` or
``Permission()``, an unknown ``match`` mode, or a non-callable predicate raises
``ValueError`` or ``TypeError`` instead of producing an always-deny rule.

Declaring requirements on a view
--------------------------------

Requirements are class attributes on an admin view. They are declarative and do
not use route decorators::

    from flask_exts.admin.sqla.view import SqlaModelView
    from flask_exts.security.authorizer.rbac_authorizer import (
        All,
        Permission,
        Predicate,
        Role,
    )


    class TicketView(SqlaModelView):
        permission = All(Role("editor"), Predicate(owns_ticket))
        permissions = {"delete": Permission("ticket:delete")}
        roles = ("admin", "support")

The authorizer resolves declarations in this order:

1. ``permissions[fn.__name__]`` for the method being called, when ``fn`` is
   known and the mapping contains that name.
2. ``permission`` for the whole view.
3. ``roles`` as a role requirement.
4. ``allow_by_roles()``, which keeps the ``admin`` / ``role_need`` rules
   working for views that declare nothing.

A bare string is shorthand for ``Role``: ``permission = "admin"`` is the same
as ``permission = Role("admin")``. An unsupported declaration type raises
``TypeError``.

Identity data
-------------

``RBACAuthorizer`` reads roles and permissions from one of these sources, in
order:

1. ``user_data_loader`` returning a mapping such as
   ``{"roles": [...], "permissions": [...]}``.
2. ``role_loader`` and ``permission_loader``, which return the current user's
   names.
3. The user object's ``get_roles()`` and ``get_permissions()`` methods.

If none is available the sets are empty, so role and permission requirements
fail closed. Loaders are application code: do not build their return value from
untrusted request data.

Guarantees and limits
---------------------

Every authorizer applies the shared view login gate before its own rules:

- An authenticated, active user with the ``admin`` role passes every view
  without evaluating its requirements. The ``admin`` role is the only built-in
  superuser; other roles need an explicit requirement or ``role_need`` match.
  The shortcut reads ``user.get_roles()`` only; loader-provided roles and
  predicates are not consulted for it.
- On a public view (``allow_access = True``), only methods named in
  ``login_required_functions`` require a logged-in user; those methods return
  the view's 403 response for anonymous requests.
- On a non-public view, an anonymous request is denied before any requirement
  runs.
- An authenticated user with ``is_active = False`` is denied before the
  requirement is evaluated.
- A public view short-circuits requirements entirely. Keep
  ``allow_access = True`` for login, registration and other genuinely public
  endpoints, not for pages that should be protected by a requirement.

When no view is supplied, the authorizer skips the login gate and falls back to
``allow_by_roles()``. This is the path used by direct ``authorize_allow()``
calls in API code.

Query helpers
-------------

``RBACAuthorizer`` also exposes ``can(*requirements, **kwargs)``,
``has_role(name, user=None)``, ``has_permission(name, user=None)`` and
``build_context(user, view=None, fn=None, **kwargs)``. These helpers evaluate
requirements or loaded names only; they do not apply the route login gate, the
``admin`` superuser shortcut, or the ``is_active`` check. Call ``allow()`` (or
enforce the same checks) when the result decides whether a request may
proceed.
