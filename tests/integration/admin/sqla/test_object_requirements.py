import pytest

from flask_exts.admin.sqla.inline.inline_model_convert import InlineForm
from flask_exts.datastore.sqla import db
from flask_exts.proxies import current_userstore
from flask_exts.security.authorizer.rbac_authorizer import (
    Authenticated,
    Predicate,
    RBACAuthorizer,
)

from .models.admin_records import AdminTestModel, RelatedAdminTestModel
from .models.one_to_many import OneToManyParentModel


@pytest.fixture
def rbac_authorizer(app):
    """Replace the default simple authorizer for object-level checks."""
    security = app.extensions["exts"].get_extension("security").get_security()
    authorizer = RBACAuthorizer()
    security._registry.register("authorizer", authorizer)
    return authorizer


def login_non_admin(client):
    """Log in an authenticated, non-admin user for object checks."""
    user = current_userstore.create_user(
        username="object_viewer",
        password="object_password",
        email="object_viewer@example.com",
    )
    with client.session_transaction() as sess:
        sess["_user_id"] = user.get_id()
        sess["_fresh"] = True
    return user


def test_single_object_entries_check_resolved_object(
    app, client, admin, sqla_view_factory, rbac_authorizer
):
    with app.app_context():
        db.reset_all()
        allowed = OneToManyParentModel()
        denied = OneToManyParentModel()
        db.session.add_all([allowed, denied])
        db.session.commit()
        allowed_id = allowed.id
        denied_id = denied.id

        requirement = Predicate(lambda ctx: ctx.object.id == allowed_id)
        view = sqla_view_factory(
            OneToManyParentModel,
            endpoint="object_single",
            permission=Authenticated(),
            object_requirements={
                "details_view": requirement,
                "edit_view": requirement,
                "delete_view": requirement,
            },
            object_requirement_exempt=("action_view",),
        )
        admin.register_view(view)
        login_non_admin(client)

    assert (
        client.get(f"/admin/object_single/details/?id={allowed_id}").status_code == 200
    )
    assert (
        client.get(f"/admin/object_single/details/?id={denied_id}").status_code == 403
    )
    assert client.get(f"/admin/object_single/edit/?id={allowed_id}").status_code == 200
    assert client.get(f"/admin/object_single/edit/?id={denied_id}").status_code == 403

    rv = client.post("/admin/object_single/delete/", data={"id": denied_id})
    assert rv.status_code == 403
    with app.app_context():
        assert db.session.get(OneToManyParentModel, denied_id) is not None

    rv = client.post("/admin/object_single/delete/", data={"id": allowed_id})
    assert rv.status_code == 302
    with app.app_context():
        assert db.session.get(OneToManyParentModel, allowed_id) is None


def test_ajax_update_checks_resolved_object(
    app, client, admin, sqla_view_factory, rbac_authorizer
):
    with app.app_context():
        db.reset_all()
        allowed = AdminTestModel(name="allowed")
        denied = AdminTestModel(name="denied")
        db.session.add_all([allowed, denied])
        db.session.commit()
        allowed_id = allowed.id
        denied_id = denied.id

        view = sqla_view_factory(
            AdminTestModel,
            endpoint="object_ajax_update",
            permission=Authenticated(),
            column_editable_list=["name"],
            object_requirements={
                "ajax_update": Predicate(lambda ctx: ctx.object.id == allowed_id)
            },
            object_requirement_exempt=("action_view", "delete_view"),
        )
        admin.register_view(view)
        login_non_admin(client)

    rv = client.post(
        "/admin/object_ajax_update/ajax/update/",
        json={"pk": str(denied_id), "name": "changed"},
    )
    assert rv.status_code == 403
    with app.app_context():
        assert db.session.get(AdminTestModel, denied_id).name == "denied"

    rv = client.post(
        "/admin/object_ajax_update/ajax/update/",
        json={"pk": str(allowed_id), "name": "changed"},
    )
    assert rv.status_code == 200
    with app.app_context():
        assert db.session.get(AdminTestModel, allowed_id).name == "changed"


def test_action_view_checks_every_selected_object(
    app, client, admin, sqla_view_factory, rbac_authorizer
):
    with app.app_context():
        db.reset_all()
        allowed = AdminTestModel(name="allowed")
        denied = AdminTestModel(name="denied")
        db.session.add_all([allowed, denied])
        db.session.commit()
        allowed_id = allowed.id
        denied_id = denied.id

        view = sqla_view_factory(
            AdminTestModel,
            endpoint="object_action",
            permission=Authenticated(),
            object_requirements={
                "action_view": Predicate(lambda ctx: ctx.object.id == allowed_id)
            },
            object_requirement_exempt=("delete_view",),
        )
        admin.register_view(view)
        login_non_admin(client)

    rv = client.post(
        "/admin/object_action/action/",
        data={"action": "delete", "rowid": [allowed_id, denied_id]},
    )
    assert rv.status_code == 403
    with app.app_context():
        assert db.session.get(AdminTestModel, allowed_id) is not None
        assert db.session.get(AdminTestModel, denied_id) is not None

    rv = client.post(
        "/admin/object_action/action/",
        data={"action": "delete", "rowid": [allowed_id]},
    )
    assert rv.status_code == 302
    with app.app_context():
        assert db.session.get(AdminTestModel, allowed_id) is None
        assert db.session.get(AdminTestModel, denied_id) is not None


def test_ajax_inline_model_checks_parent_and_child(
    app, client, admin, sqla_view_factory, rbac_authorizer
):
    with app.app_context():
        db.reset_all()
        allowed = AdminTestModel(name="allowed")
        denied = AdminTestModel(name="denied")
        db.session.add_all([allowed, denied])
        db.session.commit()
        allowed_id = allowed.id
        denied_id = denied.id

        def owns_record(ctx):
            obj = ctx.object
            return (
                getattr(obj, "id", None) == allowed_id
                or getattr(obj, "admin_record_id", None) == allowed_id
            )

        denied_child = RelatedAdminTestModel(
            optional_string="denied child", admin_record=denied
        )
        db.session.add(denied_child)
        db.session.commit()
        denied_child_id = denied_child.id

        view = sqla_view_factory(
            AdminTestModel,
            endpoint="object_inline",
            permission=Authenticated(),
            inline_models=(
                InlineForm(
                    RelatedAdminTestModel,
                    form_columns=("optional_string",),
                ),
            ),
            object_requirements={"ajax_inline_model": Predicate(owns_record)},
            object_requirement_exempt=("action_view", "delete_view"),
        )
        admin.register_view(view)
        view.edit_form(obj=allowed)
        login_non_admin(client)

    rv = client.post(
        "/admin/object_inline/ajax/inline/related_records/",
        json={
            "action": "save",
            "parent_id": denied_id,
            "values": {"optional_string": "blocked"},
        },
    )
    assert rv.status_code == 403
    with app.app_context():
        assert db.session.query(RelatedAdminTestModel).count() == 1
        assert (
            db.session.query(RelatedAdminTestModel)
            .filter_by(optional_string="blocked")
            .count()
            == 0
        )

    rv = client.post(
        "/admin/object_inline/ajax/inline/related_records/",
        json={
            "action": "save",
            "parent_id": allowed_id,
            "values": {"optional_string": "created"},
        },
    )
    assert rv.status_code == 200
    created_child_id = rv.json["child_id"]
    with app.app_context():
        child = db.session.get(RelatedAdminTestModel, created_child_id)
        assert child.optional_string == "created"

    rv = client.post(
        "/admin/object_inline/ajax/inline/related_records/",
        json={
            "action": "save",
            "parent_id": denied_id,
            "child_id": denied_child_id,
            "values": {"optional_string": "blocked update"},
        },
    )
    assert rv.status_code == 403
    with app.app_context():
        assert (
            db.session.get(RelatedAdminTestModel, denied_child_id).optional_string
            == "denied child"
        )

    rv = client.post(
        "/admin/object_inline/ajax/inline/related_records/",
        json={
            "action": "delete",
            "parent_id": denied_id,
            "child_id": denied_child_id,
        },
    )
    assert rv.status_code == 403
    with app.app_context():
        assert db.session.get(RelatedAdminTestModel, denied_child_id) is not None

    rv = client.post(
        "/admin/object_inline/ajax/inline/related_records/",
        json={
            "action": "save",
            "parent_id": allowed_id,
            "child_id": created_child_id,
            "values": {"optional_string": "updated"},
        },
    )
    assert rv.status_code == 200
    with app.app_context():
        assert (
            db.session.get(RelatedAdminTestModel, created_child_id).optional_string
            == "updated"
        )

    rv = client.post(
        "/admin/object_inline/ajax/inline/related_records/",
        json={
            "action": "delete",
            "parent_id": allowed_id,
            "child_id": created_child_id,
        },
    )
    assert rv.status_code == 200
    with app.app_context():
        assert db.session.get(RelatedAdminTestModel, created_child_id) is None


def test_startup_rejects_capabilities_without_object_requirements(
    app, sqla_view_factory
):
    with app.app_context():
        predicate = Predicate(lambda ctx: True)

        with pytest.raises(ValueError, match="column_editable_list"):
            sqla_view_factory(
                AdminTestModel,
                permission=predicate,
                column_editable_list=["name"],
            )

        with pytest.raises(ValueError, match="inline_models"):
            sqla_view_factory(
                AdminTestModel,
                permission=predicate,
                inline_models=(InlineForm(RelatedAdminTestModel),),
            )

        with pytest.raises(ValueError, match="bulk actions"):
            sqla_view_factory(AdminTestModel, permission=predicate)


def test_startup_rejects_any_mode_for_write_entries(app, sqla_view_factory):
    with (
        app.app_context(),
        pytest.raises(ValueError, match="cannot use the 'any' object mode"),
    ):
        sqla_view_factory(
            AdminTestModel,
            permission=Predicate(lambda ctx: True),
            column_editable_list=["name"],
            object_requirements={"ajax_update": Predicate(lambda ctx: True)},
            object_requirement_modes={"ajax_update": "any"},
            object_requirement_exempt=("action_view",),
        )
