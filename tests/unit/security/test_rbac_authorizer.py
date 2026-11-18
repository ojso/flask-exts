"""Tests for the Flask-RPBAC style requirement model and its authorizer."""

import pytest

from flask_exts.security.authorizer.rbac_authorizer import (
    All,
    Any,
    Authenticated,
    BuildContext,
    Not,
    Permission,
    Predicate,
    RBACAuthorizer,
    Requirements,
    Role,
)
from flask_exts.security.registry import Registry


class MockUser:
    """Minimal user implementing the attributes the authorizer reads."""

    def __init__(
        self,
        roles=None,
        permissions=None,
        is_active=True,
        is_authenticated=True,
    ):
        self._roles = roles or []
        self._permissions = permissions or []
        self.is_active = is_active
        self.is_authenticated = is_authenticated
        self.id = 7

    def get_roles(self):
        return self._roles

    def get_permissions(self):
        return self._permissions


class FakeApp:
    """Only provides the config interface needed by the registry."""

    def __init__(self, config=None):
        self.config = config or {}


def make_view(**attrs):
    return type("View", (), attrs)()


def make_authorizer():
    authorizer = RBACAuthorizer()
    authorizer.init_app(FakeApp())
    return authorizer


def ctx(user=None, roles=(), permissions=(), **kwargs):
    return BuildContext(
        user=user or MockUser(),
        roles=set(roles),
        permissions=set(permissions),
        kwargs=kwargs,
    )


class TestRole:
    """``Role`` follows Flask-RPBAC: any by default, all on request."""

    def test_single_role(self):
        assert Role("admin").check(ctx(roles=["admin"])) is True
        assert Role("admin").check(ctx(roles=["editor"])) is False

    def test_any_match_is_the_default(self):
        requirement = Role("admin", "editor")
        assert requirement.match == "any"
        assert requirement.check(ctx(roles=["editor"])) is True

    def test_all_match_requires_every_role(self):
        requirement = Role("admin", "editor", match="all")
        assert requirement.check(ctx(roles=["admin"])) is False
        assert requirement.check(ctx(roles=["admin", "editor"])) is True

    def test_empty_role_set_is_rejected(self):
        with pytest.raises(ValueError):
            Role()

    def test_unknown_match_mode_is_rejected(self):
        with pytest.raises(ValueError):
            Role("admin", match="most")


class TestPermission:
    """``Permission`` follows Flask-RPBAC: all by default, any on request."""

    def test_all_match_is_the_default(self):
        requirement = Permission("post:read", "post:write")
        assert requirement.match == "all"
        assert requirement.check(ctx(permissions=["post:read"])) is False
        assert requirement.check(ctx(permissions=["post:read", "post:write"])) is True

    def test_any_match(self):
        requirement = Permission("post:read", "post:write", match="any")
        assert requirement.check(ctx(permissions=["post:write"])) is True

    def test_missing_permission_is_denied(self):
        assert Permission("post:write").check(ctx(permissions=[])) is False


class TestPredicate:
    """``Predicate`` receives the build context for object-level checks."""

    def test_receives_kwargs_and_pstore(self):
        def owns(ctx):
            ctx.pstore["owner"] = ctx.kwargs["post_id"]
            return ctx.kwargs["post_id"] == 42

        assert Predicate(owns).check(ctx(post_id=42)) is True
        assert Predicate(owns).check(ctx(post_id=1)) is False

    def test_receives_view(self):
        view = make_view(ticket_owner_id=7)
        requirement = Predicate(lambda context: context.view.ticket_owner_id == 7)
        build = BuildContext(user=MockUser(), view=view)
        assert requirement.check(build) is True

    def test_non_callable_is_rejected(self):
        with pytest.raises(TypeError):
            Predicate(123)


class TestComposition:
    """``All``, ``Any``, ``Not`` and the operators mirror Flask-RPBAC."""

    def test_all_requires_every_child(self):
        requirement = All(Role("admin"), Permission("post:write"))
        assert requirement.check(ctx(roles=["admin"], permissions=["post:write"]))
        assert not requirement.check(ctx(roles=["admin"]))

    def test_any_needs_one_child(self):
        requirement = Any(Role("admin"), Permission("post:read"))
        assert requirement.check(ctx(permissions=["post:read"]))
        assert not requirement.check(ctx(roles=["editor"]))

    def test_not_inverts(self):
        assert Not(Role("admin")).check(ctx(roles=["editor"])) is True
        assert Not(Role("admin")).check(ctx(roles=["admin"])) is False

    def test_operators_build_composites(self):
        combined = Role("admin") | Permission("post:read")
        assert isinstance(combined, Any)
        assert combined.check(ctx(permissions=["post:read"]))

        strict = Role("admin") & Permission("post:write")
        assert isinstance(strict, All)
        assert not strict.check(ctx(roles=["admin"]))

    def test_authenticated(self):
        assert Authenticated().check(ctx()) is True
        assert (
            Authenticated().check(ctx(user=MockUser(is_authenticated=False))) is False
        )

    def test_requirements_is_abstract(self):
        with pytest.raises(TypeError):
            Requirements()


class TestViewDeclarations:
    """Views declare requirements as class attributes, without decorators."""

    def test_permission_attribute(self):
        view = make_view(permission=All(Role("admin"), Permission("post:write")))
        user = MockUser(["admin"], ["post:write"])
        assert make_authorizer().allow(user=user, view=view) is True

    def test_permission_denies_when_requirement_fails(self):
        view = make_view(permission=Permission("post:write"))
        assert make_authorizer().allow(user=MockUser(["editor"]), view=view) is False

    def test_admin_role_passes_before_permission_requirements(self):
        view = make_view(permission=Permission("post:write"))
        user = MockUser(["admin"])
        assert make_authorizer().allow(user=user, view=view) is True

    def test_roles_attribute_uses_role_requirement(self):
        view = make_view(roles=("admin", "support"))
        assert make_authorizer().allow(user=MockUser(["support"]), view=view) is True

    def test_string_shorthand_means_role(self):
        view = make_view(permission="admin")
        assert make_authorizer().allow(user=MockUser(["admin"]), view=view) is True

    def test_function_entry_overrides_view_default(self):
        def delete(self):
            return "deleted"

        view = make_view(
            permissions={"delete": Permission("ticket:delete")},
            permission=Role("support"),
        )
        user = MockUser(["support"])
        assert make_authorizer().allow(user=user, view=view, fn=delete) is False
        assert make_authorizer().allow(user=user, view=view) is True

    def test_unsupported_declaration_is_rejected(self):
        view = make_view(permission=123)
        with pytest.raises(TypeError):
            make_authorizer().allow(user=MockUser(), view=view)


class TestLoaders:
    """Roles and permissions come from loaders or the user object."""

    def test_role_and_permission_loaders_are_used(self):
        authorizer = make_authorizer()
        authorizer.role_loader(lambda: ["admin"])
        authorizer.permission_loader(lambda: ["post:write"])

        view = make_view(permission=All(Role("admin"), Permission("post:write")))
        user = MockUser(["nobody"], [])
        assert authorizer.allow(user=user, view=view) is True

    def test_user_data_loader_takes_precedence(self):
        authorizer = make_authorizer()
        authorizer.role_loader(lambda: ["editor"])
        authorizer.user_data_loader(
            lambda: {"roles": ["admin"], "permissions": ["post:write"]}
        )

        assert authorizer.has_role("admin") is True
        assert authorizer.has_role("editor") is False
        assert authorizer.has_permission("post:write") is True

    def test_user_without_getters_has_nothing(self):
        class Bare:
            is_active = True

        authorizer = make_authorizer()
        assert authorizer.build_context(Bare()).roles == set()
        assert authorizer.build_context(Bare()).permissions == set()


class TestAuthorizerApi:
    """``can``, ``has_role`` and ``has_permission`` are query helpers."""

    def test_can_with_multiple_requirements(self):
        authorizer = make_authorizer()
        user = MockUser(["admin"], ["post:write"])
        assert authorizer.can(Role("admin"), Permission("post:write"), user=user)
        assert not authorizer.can(Role("admin"), Permission("post:delete"), user=user)

    def test_has_role_and_permission(self):
        user = MockUser(["admin"], ["post:read"])
        authorizer = make_authorizer()
        assert authorizer.has_role("admin", user) is True
        assert authorizer.has_permission("post:read", user) is True
        assert authorizer.has_permission("post:write", user) is False


class TestExistingGuarantees:
    """Behaviour that must not regress when switching authorizers."""

    def test_allow_access_precedes_everything(self):
        view = make_view(allow_access=True, permission=Role("admin"))
        user = MockUser(is_active=False)
        assert make_authorizer().allow(user=user, view=view) is True

    def test_inactive_user_denied_even_when_requirement_passes(self):
        view = make_view(permission=Role("support"))
        user = MockUser(["support"], is_active=False)
        assert make_authorizer().allow(user=user, view=view) is False

    def test_undeclared_view_falls_back_to_admin_only(self):
        view = make_view()
        assert make_authorizer().allow(user=MockUser(["admin"]), view=view) is True
        assert make_authorizer().allow(user=MockUser(["editor"]), view=view) is False

    def test_missing_view_falls_back_to_admin_only(self):
        assert make_authorizer().allow(user=MockUser(["admin"])) is True
        assert make_authorizer().allow(user=MockUser(["editor"])) is False

    def test_login_required_functions_deny_anonymous_before_requirements(self):
        def index(self):
            return "index"

        index.__name__ = "index"
        view = make_view(
            allow_access=True,
            login_required_functions=("index",),
            permission=Role("admin"),
        )
        user = MockUser(["admin"], is_authenticated=False)

        assert make_authorizer().allow(user=user, view=view, fn=index) is False

        user.is_authenticated = True
        assert make_authorizer().allow(user=user, view=view, fn=index) is True

    def test_public_view_allows_anonymous_unlisted_method(self):
        def other(self):
            return "other"

        other.__name__ = "other"
        view = make_view(allow_access=True, login_required_functions=("index",))

        assert (
            make_authorizer().allow(
                user=MockUser(is_authenticated=False), view=view, fn=other
            )
            is True
        )

    def test_non_public_view_requires_authentication(self):
        view = make_view(allow_access=False, permission=Role("admin"))
        user = MockUser(["admin"], is_authenticated=False)

        assert make_authorizer().allow(user=user, view=view) is False

        user.is_authenticated = True
        assert make_authorizer().allow(user=user, view=view) is True


class TestRegistrySelection:
    """The config value decides which authorizer is registered."""

    def test_default_is_simple_authorizer(self):
        from flask_exts.security.authorizer.simple_authorizer import (
            SimpleAuthorizer,
        )

        registry = Registry()
        registry.init_all(FakeApp())
        assert isinstance(registry.get("authorizer"), SimpleAuthorizer)

    def test_rbac_is_selected_by_config(self):
        registry = Registry()
        registry.init_all(FakeApp({"SECURITY_AUTHORIZER": "rbac"}))
        assert isinstance(registry.get("authorizer"), RBACAuthorizer)

    def test_unknown_name_is_rejected(self):
        registry = Registry()
        with pytest.raises(ValueError):
            registry.init_all(FakeApp({"SECURITY_AUTHORIZER": "typo"}))
