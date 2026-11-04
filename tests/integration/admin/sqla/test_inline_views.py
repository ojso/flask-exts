from datetime import datetime

from flask import render_template_string

from flask_exts.admin.sqla.inline.inline_model_convert import InlineForm
from flask_exts.datastore.sqla import db

from .models.inline_datetime import InlineDateTimeChildModel, InlineDateTimeParentModel
from .models.multiple_foreign_keys import (
    MultipleForeignKeyChildModel,
    MultipleForeignKeyTargetModel,
)
from .models.one_to_many import (
    OneToManyBackPopulatedChildModel,
    OneToManyParentModel,
)


class TestInlineModelIntegration:
    """Integration tests: HTTP create/edit with inline models."""

    def test_inline_create_page_renders(
        self, app, admin, client, login_as_admin, sqla_view_factory
    ):
        """Test creating a parent page renders with inline fields."""
        with app.app_context():
            db.reset_all()
            login_as_admin()

            view = sqla_view_factory(
                OneToManyParentModel,
                endpoint="inline_create",
                inline_models=(OneToManyBackPopulatedChildModel,),
            )
            admin.register_view(view)

        rv = client.get("/admin/inline_create/new/")
        assert rv.status_code == 200

    def test_inline_edit_page_renders_with_existing_children(
        self, app, admin, client, login_as_admin, sqla_view_factory
    ):
        """Test editing a parent with existing inline children renders."""
        with app.app_context():
            db.reset_all()
            login_as_admin()

            view = sqla_view_factory(
                OneToManyParentModel,
                endpoint="inline_edit",
                inline_models=(OneToManyBackPopulatedChildModel,),
            )
            admin.register_view(view)

            # Create parent with children
            parent = OneToManyParentModel()
            OneToManyBackPopulatedChildModel(parent=parent)
            db.session.add(parent)
            db.session.commit()
            parent_id = parent.id

        rv = client.get(f"/admin/inline_edit/edit/?id={parent_id}")
        assert rv.status_code == 200

    def test_create_parent_without_inline_data(
        self, app, client, admin, login_as_admin, sqla_view_factory
    ):
        """Test POST to create a parent (without inline data)."""
        with app.app_context():
            db.reset_all()
            view = sqla_view_factory(
                OneToManyParentModel,
                endpoint="inline_post",
                inline_models=(OneToManyBackPopulatedChildModel,),
            )
            admin.register_view(view)

            login_as_admin()

        rv = client.post(
            "/admin/inline_post/new/",
            data={},
            follow_redirects=True,
        )
        assert rv.status_code == 200

    def test_multiple_foreign_key_inline_create_page(
        self, app, client, admin, login_as_admin, sqla_view_factory
    ):
        """Test creating a parent model with a related inline child."""
        with app.app_context():
            db.reset_all()

            view = sqla_view_factory(
                MultipleForeignKeyTargetModel,
                endpoint="inline_bc_page",
                inline_models=(MultipleForeignKeyChildModel,),
            )
            admin.register_view(view)

            login_as_admin()

        rv = client.get("/admin/inline_bc_page/new/")
        assert rv.status_code == 200

    def test_inline_rows_show_primary_key_or_new_marker(
        self, app, admin, sqla_view_factory
    ):
        """Persisted rows show their primary key; unsaved rows show New."""
        with app.app_context():
            db.reset_all()

            view = sqla_view_factory(
                OneToManyParentModel,
                endpoint="inline_marker",
                inline_models=(OneToManyBackPopulatedChildModel,),
            )
            admin.register_view(view)

            parent = OneToManyParentModel()
            child = OneToManyBackPopulatedChildModel(parent=parent)
            db.session.add(parent)
            db.session.commit()

            form = view.edit_form(obj=parent)
            with app.test_request_context("/admin/inline_marker/edit/"):
                html = render_template_string(
                    "{% from 'macro/form.html' import render_form_fields %}"
                    "{{ render_form_fields(form, view=view) }}",
                    form=form,
                    view=view,
                )

            assert f">{child.id}</span>" in html
            assert ">New</span>" in html

    def test_inline_datetime_form_value_coercion(self, app, admin, sqla_view_factory):
        """Inline values are coerced by the child form before persistence."""
        with app.app_context():
            db.reset_all()

            parent = InlineDateTimeParentModel()
            db.session.add(parent)
            db.session.commit()

            view = sqla_view_factory(
                InlineDateTimeParentModel,
                endpoint="inline_datetime",
                inline_models=(
                    InlineForm(InlineDateTimeChildModel, form_columns=("occurred_at",)),
                ),
            )
            admin.register_view(view)
            view.edit_form(obj=parent)

            child_id = view.save_inline_child(
                parent,
                "children",
                None,
                {"id": "", "occurred_at": "2026-10-31T11:11"},
            )
            child = db.session.get(InlineDateTimeChildModel, int(child_id))
            assert child is not None
            assert child.occurred_at == datetime(2026, 10, 31, 11, 11)
