import re
from datetime import datetime

from flask import session

from flask_exts.admin.sqla.inline.inline_model_convert import InlineForm
from flask_exts.datastore.sqla import db
from flask_exts.forms.fields.ajax_select import AjaxSelectField
from flask_exts.forms.form.csrf import get_csrf_token

from .models.admin_records import (
    AdminTestModel,
    NestedAdminTestModel,
    RelatedAdminTestModel,
)
from .models.inline_datetime import InlineDateTimeChildModel, InlineDateTimeParentModel
from .models.multiple_foreign_keys import (
    MultipleForeignKeyChildModel,
    MultipleForeignKeyTargetModel,
)
from .models.one_to_many import (
    OneToManyBackPopulatedChildModel,
    OneToManyParentModel,
)
from .models.one_to_one import OneToOneChildModel, OneToOneParentModel


class TestInlineModelIntegration:
    """Integration tests: HTTP create/edit with inline models."""

    def test_ajax_inline_datetime_value_coercion(
        self, app, admin, client, login_as_admin, sqla_view_factory
    ):
        """The AJAX endpoint coerces datetime strings before persisting."""
        with app.app_context():
            db.reset_all()
            parent = InlineDateTimeParentModel()
            db.session.add(parent)
            db.session.commit()
            parent_id = parent.id

            view = sqla_view_factory(
                InlineDateTimeParentModel,
                endpoint="inline_datetime_ajax",
                inline_models=(
                    InlineForm(InlineDateTimeChildModel, form_columns=("occurred_at",)),
                ),
            )
            admin.register_view(view)

            login_as_admin()

        rv = client.post(
            "/admin/inline_datetime_ajax/ajax/inline/children/",
            json={
                "action": "save",
                "parent_id": parent_id,
                "values": {"id": "", "occurred_at": "2026-10-31T11:11"},
            },
        )
        assert rv.status_code == 200

        with app.app_context():
            child = db.session.get(InlineDateTimeChildModel, rv.json["child_id"])
            assert child is not None
            assert child.occurred_at == datetime(2026, 10, 31, 11, 11)

    def test_ajax_inline_row_crud(
        self, app, client, admin, login_as_admin, sqla_view_factory
    ):
        """Test parent-first AJAX and independent inline row persistence."""
        with app.app_context():
            db.reset_all()

            view = sqla_view_factory(
                MultipleForeignKeyTargetModel,
                endpoint="inline_crud",
                inline_models=(MultipleForeignKeyChildModel,),
            )
            admin.register_view(view)

            login_as_admin()

        rv = client.post(
            "/admin/inline_crud/ajax/create-parent/",
            data={
                "name": "parent",
                "kind": "kind",
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        parent_id = rv.json["id"]

        endpoint = "/admin/inline_crud/ajax/inline/children/"
        rv = client.post(
            endpoint,
            json={
                "action": "save",
                "parent_id": parent_id,
                "values": {"name": "first child", "quantity": "7"},
            },
        )
        assert rv.status_code == 200
        child_id = rv.json["child_id"]

        with app.app_context():
            child = db.session.get(MultipleForeignKeyChildModel, child_id)
            assert child.name == "first child"
            assert child.quantity == 7

        rv = client.post(
            endpoint,
            json={
                "action": "save",
                "parent_id": parent_id,
                "child_id": child_id,
                "values": {
                    "id": str(child_id),
                    "name": "updated child",
                    "quantity": "8",
                },
            },
        )
        assert rv.status_code == 200

        with app.app_context():
            child = db.session.get(MultipleForeignKeyChildModel, child_id)
            assert child.name == "updated child"
            assert child.quantity == 8

        rv = client.post(
            endpoint,
            json={
                "action": "delete",
                "parent_id": parent_id,
                "child_id": child_id,
            },
        )
        assert rv.status_code == 200

        with app.app_context():
            assert db.session.get(MultipleForeignKeyChildModel, child_id) is None

        rv = client.post(
            endpoint,
            json={
                "action": "delete",
                "parent_id": parent_id,
                "child_id": 999,
            },
        )
        assert rv.status_code == 404

    def test_ajax_one_to_one_inline_relationship_crud(
        self, app, client, admin, sqla_view_factory, login_as_admin
    ):
        """Test AJAX create/update/delete for a scalar inline relationship."""
        with app.app_context():
            db.reset_all()

            view = sqla_view_factory(
                OneToOneParentModel,
                endpoint="inline_o2o_delete",
                inline_models=(InlineForm(OneToOneChildModel),),
            )
            admin.register_view(view)

            parent = OneToOneParentModel()
            child = OneToOneChildModel(name="existing", parent=parent)
            db.session.add(parent)
            db.session.commit()
            parent_id = parent.id
            child_id = child.id

            login_as_admin()

        edit_page = client.get(f"/admin/inline_o2o_delete/edit/?id={parent_id}")
        assert edit_page.status_code == 200
        html = edit_page.get_data(as_text=True)
        assert "inline-model-row-template" in html
        assert re.search(
            r'<input\b(?=[^>]*\bname="child-0-name")'
            r'(?=[^>]*\bform="inline-model-ajax-only")[^>]*>',
            html,
        )
        assert 'id="inline-model-ajax-only"' not in html

        rv = client.post(
            "/admin/inline_o2o_delete/ajax/inline/child/",
            json={
                "action": "save",
                "parent_id": parent_id,
                "child_id": child_id,
                "values": {"name": "changed"},
            },
        )
        assert rv.status_code == 200

        with app.app_context():
            child = db.session.get(OneToOneChildModel, child_id)
            assert child.name == "changed"

        rv = client.post(
            "/admin/inline_o2o_delete/ajax/inline/child/",
            json={
                "action": "delete",
                "parent_id": parent_id,
                "child_id": child_id,
            },
        )
        assert rv.status_code == 200
        with app.app_context():
            assert db.session.get(OneToOneChildModel, child_id) is None
            assert db.session.get(OneToOneParentModel, parent_id).child is None

    def test_ajax_inline_requires_csrf_token(
        self, app, client, admin, login_as_admin, sqla_view_factory
    ):
        """Inline AJAX mutations require the configured CSRF token."""
        app.config["CSRF_ENABLED"] = True
        with app.app_context():
            db.reset_all()

            view = sqla_view_factory(
                OneToManyParentModel,
                endpoint="inline_csrf",
                inline_models=(OneToManyBackPopulatedChildModel,),
            )
            admin.register_view(view)
            parent = OneToManyParentModel()
            child = OneToManyBackPopulatedChildModel(parent=parent)
            db.session.add(parent)
            db.session.commit()
            parent_id = parent.id
            child_id = child.id

            login_as_admin()

        with app.test_request_context():
            token = get_csrf_token()
            session_csrf_token = session.get("csrf_token")
        with client.session_transaction() as sess:
            sess["csrf_token"] = session_csrf_token

        rv = client.get(f"/admin/inline_csrf/edit/?id={parent_id}")
        assert rv.status_code == 200

        rv = client.post(
            "/admin/inline_csrf/ajax/inline/back_populated_children/",
            json={
                "action": "delete",
                "parent_id": parent_id,
                "child_id": child_id,
            },
        )
        assert rv.status_code == 400

        rv = client.post(
            "/admin/inline_csrf/ajax/inline/back_populated_children/",
            json={
                "action": "delete",
                "parent_id": parent_id,
                "child_id": child_id,
                "csrf_token": token,
            },
        )
        assert rv.status_code == 200

        with app.app_context():
            assert db.session.get(OneToManyBackPopulatedChildModel, child_id) is None

    def test_inline_form_ajax_refs_registers_loader(
        self, app, client, admin, login_as_admin, sqla_view_factory
    ):
        """InlineForm.ajax_refs registers a loader the child form can use."""
        with app.app_context():
            db.reset_all()
            nested = NestedAdminTestModel(value="nested record")
            parent = AdminTestModel(name="parent")
            child = RelatedAdminTestModel(
                optional_string="child",
                nested_record=nested,
                admin_record=parent,
            )
            db.session.add_all([nested, parent, child])
            db.session.commit()
            parent_id = parent.id
            nested_id = nested.id

            view = sqla_view_factory(
                AdminTestModel,
                endpoint="inline_ajax_refs",
                inline_models=(
                    InlineForm(
                        RelatedAdminTestModel,
                        form_columns=("optional_string", "nested_record"),
                        ajax_refs={"nested_record": {"fields": ("value",)}},
                    ),
                ),
            )
            admin.register_view(view)

            form = view.edit_form(obj=parent)
            child_field = form.related_records.form_class().nested_record
            loader_name = "relatedadmintestmodel-nested_record"
            assert isinstance(child_field, AjaxSelectField)
            assert child_field.loader is view.get_ajax_loader(loader_name)
            assert child_field.loader.name == loader_name

            login_as_admin()

        rv = client.get(f"/admin/inline_ajax_refs/edit/?id={parent_id}")
        assert rv.status_code == 200
        assert loader_name in rv.get_data(as_text=True)

        rv = client.get(
            "/admin/inline_ajax_refs/ajax/lookup/",
            query_string={"name": loader_name, "query": "nested"},
        )
        assert rv.status_code == 200
        rows = rv.json
        assert [row[0] for row in rows] == [nested_id]
        assert isinstance(rows[0][1], str)
        assert rows[0][1]

    def test_inline_form_ajax_refs_persists_related_value(
        self, app, client, admin, login_as_admin, sqla_view_factory
    ):
        """Saving an inline row through AJAX stores the AJAX-related foreign key."""
        with app.app_context():
            db.reset_all()
            nested = NestedAdminTestModel(value="nested record")
            parent = AdminTestModel(name="parent")
            child = RelatedAdminTestModel(
                optional_string="child",
                nested_record=nested,
                admin_record=parent,
            )
            db.session.add_all([nested, parent, child])
            db.session.commit()
            parent_id = parent.id
            nested_id = nested.id
            child_id = child.id

            view = sqla_view_factory(
                AdminTestModel,
                endpoint="inline_ajax_refs_save",
                inline_models=(
                    InlineForm(
                        RelatedAdminTestModel,
                        form_columns=("optional_string", "nested_record"),
                        ajax_refs={"nested_record": {"fields": ("value",)}},
                    ),
                ),
            )
            admin.register_view(view)
            view.edit_form(obj=parent)

            login_as_admin()

        rv = client.post(
            "/admin/inline_ajax_refs_save/ajax/inline/related_records/",
            json={
                "action": "save",
                "parent_id": parent_id,
                "child_id": child_id,
                "values": {
                    "optional_string": "updated",
                    "nested_record": nested_id,
                },
            },
        )
        assert rv.status_code == 200

        with app.app_context():
            updated = db.session.get(RelatedAdminTestModel, child_id)
            assert updated.optional_string == "updated"
            assert updated.nested_record_id == nested_id
