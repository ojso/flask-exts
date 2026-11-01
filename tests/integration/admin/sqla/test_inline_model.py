from datetime import datetime

from flask import render_template_string, session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from flask_exts.admin.sqla.inline.inline_model_convert import (
    InlineForm,
    InlineOneToOneModelConverter,
)
from flask_exts.datastore.sqla import db
from flask_exts.forms.fields.inline import InlineModelField
from flask_exts.forms.form.csrf import get_csrf_token

from .models.relations import (
    ManyToOneChild2,
    ManyToOneChild3,
    ModelB,
    ModelC,
    OneToManyParent,
    OneToOneChild,
    OneToOneParent,
)


class DateTimeParent(db.Model):
    __tablename__ = "inline_datetime_parent"
    id: Mapped[int] = mapped_column(primary_key=True)
    children: Mapped[list["DateTimeChild"]] = relationship(back_populates="parent")


class DateTimeChild(db.Model):
    __tablename__ = "inline_datetime_child"
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime]
    parent_id: Mapped[int] = mapped_column(ForeignKey("inline_datetime_parent.id"))
    parent: Mapped[DateTimeParent] = relationship(back_populates="children")


class TestInlineModelConverter:
    """Test InlineModelConverter relationship discovery and form generation."""

    def test_inline_model_with_class(self, app, admin, sqla_view_factory):
        """Test inline_models with a plain model class."""
        with app.app_context():
            db.reset_all()

            view = sqla_view_factory(
                OneToManyParent,
                endpoint="inline_class",
                inline_models=(ManyToOneChild2,),
            )
            admin.register_view(view)

            form = view.create_form()
            assert hasattr(form, "children2")

    def test_inline_model_with_form_admin(self, app, admin, sqla_view_factory):
        """Test inline_models with InlineForm instance."""
        with app.app_context():
            db.reset_all()

            inline = InlineForm(ManyToOneChild2)
            view = sqla_view_factory(
                OneToManyParent,
                endpoint="inline_admin",
                inline_models=(inline,),
            )
            admin.register_view(view)

            form = view.create_form()
            assert hasattr(form, "children2")

    def test_inline_model_with_form_columns(self, app, admin, sqla_view_factory):
        """Test inline model with form_columns restriction."""
        with app.app_context():
            db.reset_all()

            inline = InlineForm(
                OneToOneChild,
                form_columns=("test",),
            )
            view = sqla_view_factory(
                OneToOneParent,
                endpoint="inline_columns",
                inline_models=(inline,),
            )
            admin.register_view(view)

            form = view.create_form()
            assert hasattr(form, "child")

    def test_inline_form_columns_retain_child_primary_key_field(
        self, app, admin, client, login_as_admin, sqla_view_factory
    ):
        """Restricted inline forms retain their PK for identifying existing rows."""
        with app.app_context():
            db.reset_all()

            parent = OneToManyParent()
            child = ManyToOneChild2(parent2=parent)
            db.session.add(parent)
            db.session.commit()
            parent_id = parent.id

            view = sqla_view_factory(
                OneToManyParent,
                endpoint="inline_columns_pk",
                inline_models=(
                    InlineForm(
                        ManyToOneChild2,
                        form_columns=(
                            "id",
                            "parent_id",
                        ),
                    ),
                ),
            )
            admin.register_view(view)

            form = view.edit_form(obj=parent)
            inline_field = form.children2
            assert "id" in inline_field.form_class()._fields
            assert inline_field.data == [child]

            login_as_admin()

        rv = client.get(f"/admin/inline_columns_pk/edit/?id={parent_id}")
        assert rv.status_code == 200
        assert 'name="children2-0-id"' in rv.get_data(as_text=True)

    def test_multiple_inline_models(self, app, admin, sqla_view_factory):
        """Test multiple inline models on a single view."""
        with app.app_context():
            db.reset_all()

            view = sqla_view_factory(
                OneToManyParent,
                endpoint="inline_multi",
                inline_models=(ManyToOneChild2, ManyToOneChild3),
            )
            admin.register_view(view)

            form = view.create_form()
            assert hasattr(form, "children2")
            assert hasattr(form, "children3")

    def test_complex_relationship_inline(self, app, admin, sqla_view_factory):
        """Test ModelC as inline of ModelB (complex relationship)."""
        with app.app_context():
            db.reset_all()

            view = sqla_view_factory(
                ModelB,
                endpoint="inline_bc",
                inline_models=(ModelC,),
            )
            admin.register_view(view)

            form = view.edit_form()
            assert hasattr(form, "c_items")


class TestInlineOneToOneModelConverter:
    """Test InlineOneToOneModelConverter for one-to-one relationships."""

    def test_one_to_one_inline(
        self, app, admin, client, login_as_admin, sqla_view_factory
    ):
        """Test one-to-one inline model form generation."""

        with app.app_context():
            db.reset_all()
            db.create_all()

            # Debug: Print relationship info
            from sqlalchemy import inspect as sa_inspect

            parent_mapper = sa_inspect(OneToOneParent)
            child_mapper = sa_inspect(OneToOneChild)

            print("OneToOneParent relationships:")
            for prop in parent_mapper.iterate_properties:
                print(
                    f"  {prop.key}: type={type(prop)}, has_direction={hasattr(prop, 'direction')}, direction={getattr(prop, 'direction', 'N/A')}"
                )

            print("\nOneToOneChild relationships:")
            for prop in child_mapper.iterate_properties:
                print(
                    f"  {prop.key}: type={type(prop)}, has_direction={hasattr(prop, 'direction')}, direction={getattr(prop, 'direction', 'N/A')}"
                )

            print(
                f"\nOneToOneParent.child: {getattr(OneToOneParent, 'child', 'NOT FOUND')}"
            )
            print(
                f"OneToOneChild.parent: {getattr(OneToOneChild, 'parent', 'NOT FOUND')}"
            )

            view = sqla_view_factory(
                OneToOneParent,
                endpoint="inline_o2o",
                inline_models=(
                    InlineForm(
                        OneToOneChild,
                        inline_model_converter=InlineOneToOneModelConverter,
                    ),
                ),
            )
            admin.register_view(view)

            form = view.edit_form()
            assert hasattr(form, "child")
            assert isinstance(form.child, InlineModelField)
            assert not form.child.is_collection


class TestInlineModelIntegration:
    """Integration tests: HTTP create/edit with inline models."""

    def test_create_page_renders(
        self, app, admin, client, login_as_admin, sqla_view_factory
    ):
        """Test creating a parent page renders with inline fields."""
        with app.app_context():
            db.reset_all()
            login_as_admin()

            view = sqla_view_factory(
                OneToManyParent,
                endpoint="inline_create",
                inline_models=(ManyToOneChild2,),
            )
            admin.register_view(view)

        rv = client.get("/admin/inline_create/new/")
        assert rv.status_code == 200

    def test_edit_page_renders_with_children(
        self, app, admin, client, login_as_admin, sqla_view_factory
    ):
        """Test editing a parent with existing inline children renders."""
        with app.app_context():
            db.reset_all()
            login_as_admin()

            view = sqla_view_factory(
                OneToManyParent,
                endpoint="inline_edit",
                inline_models=(ManyToOneChild2,),
            )
            admin.register_view(view)

            # Create parent with children
            parent = OneToManyParent()
            child = ManyToOneChild2(parent2=parent)
            db.session.add(parent)
            db.session.commit()
            parent_id = parent.id

        rv = client.get(f"/admin/inline_edit/edit/?id={parent_id}")
        assert rv.status_code == 200

    def test_post_create_with_inline(
        self, app, client, admin, login_as_admin, sqla_view_factory
    ):
        """Test POST to create a parent (without inline data)."""
        with app.app_context():
            db.reset_all()
            view = sqla_view_factory(
                OneToManyParent,
                endpoint="inline_post",
                inline_models=(ManyToOneChild2,),
            )
            admin.register_view(view)

            login_as_admin()

        rv = client.post(
            "/admin/inline_post/new/",
            data={},
            follow_redirects=True,
        )
        assert rv.status_code == 200

    def test_inline_model_b_c_create_page(
        self, app, client, admin, login_as_admin, sqla_view_factory
    ):
        """Test that the create page renders for ModelB with ModelC inline."""
        with app.app_context():
            db.reset_all()

            view = sqla_view_factory(
                ModelB,
                endpoint="inline_bc_page",
                inline_models=(ModelC,),
            )
            admin.register_view(view)

            login_as_admin()

        rv = client.get("/admin/inline_bc_page/new/")
        assert rv.status_code == 200
        # html = rv.get_data(as_text=True)
        # assert "inline-model-row-template" in html
        # assert "__prefix__-name" in html
        # assert "js/form.js" in html
        # assert "data-ajax-create-url" in html
        # assert "data-parent-unsaved" in html

    def test_inline_rows_show_pk_or_new_marker(self, app, admin, sqla_view_factory):
        """Persisted rows show their primary key; unsaved rows show New."""
        with app.app_context():
            db.reset_all()

            view = sqla_view_factory(
                OneToManyParent,
                endpoint="inline_marker",
                inline_models=(ManyToOneChild2,),
            )
            admin.register_view(view)

            parent = OneToManyParent()
            child = ManyToOneChild2(parent2=parent)
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

    def test_inline_datetime_value_is_coerced(self, app, admin, sqla_view_factory):
        """Inline values are coerced by the child form before persistence."""
        with app.app_context():
            db.reset_all()

            parent = DateTimeParent()
            db.session.add(parent)
            db.session.commit()

            view = sqla_view_factory(
                DateTimeParent,
                endpoint="inline_datetime",
                inline_models=(InlineForm(DateTimeChild, form_columns=("date",)),),
            )
            admin.register_view(view)
            view.edit_form(obj=parent)

            child_id = view.save_inline_child(
                parent,
                "children",
                None,
                {"id": "", "date": "2026-10-31T11:11"},
            )
            child = db.session.get(DateTimeChild, int(child_id))
            assert child is not None
            assert child.date == datetime(2026, 10, 31, 11, 11)

    def test_ajax_inline_datetime_value_is_coerced(
        self, app, admin, client, login_as_admin, sqla_view_factory
    ):
        """The AJAX endpoint coerces datetime strings before persisting."""
        with app.app_context():
            db.reset_all()
            parent = DateTimeParent()
            db.session.add(parent)
            db.session.commit()
            parent_id = parent.id

            view = sqla_view_factory(
                DateTimeParent,
                endpoint="inline_datetime_ajax",
                inline_models=(InlineForm(DateTimeChild, form_columns=("date",)),),
            )
            admin.register_view(view)

            login_as_admin()

        rv = client.post(
            "/admin/inline_datetime_ajax/ajax/inline/children/",
            json={
                "action": "save",
                "parent_id": parent_id,
                "values": {"id": "", "date": "2026-10-31T11:11"},
            },
        )
        assert rv.status_code == 200

        with app.app_context():
            child = db.session.get(DateTimeChild, rv.json["child_id"])
            assert child is not None
            assert child.date == datetime(2026, 10, 31, 11, 11)

    def test_ajax_create_edit_and_delete_inline_rows(
        self, app, client, admin, login_as_admin, sqla_view_factory
    ):
        """Test parent-first AJAX and independent inline row persistence."""
        with app.app_context():
            db.reset_all()

            view = sqla_view_factory(
                ModelB,
                endpoint="inline_crud",
                inline_models=(ModelC,),
            )
            admin.register_view(view)

            login_as_admin()

        rv = client.post(
            "/admin/inline_crud/ajax/create-parent/",
            data={
                "name": "parent",
                "type": "kind",
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        parent_id = rv.json["id"]

        endpoint = "/admin/inline_crud/ajax/inline/c_items/"
        rv = client.post(
            endpoint,
            json={
                "action": "save",
                "parent_id": parent_id,
                "values": {"name": "first child", "value": "7"},
            },
        )
        assert rv.status_code == 200
        child_id = rv.json["child_id"]

        with app.app_context():
            child = db.session.get(ModelC, child_id)
            assert child.name == "first child"
            assert child.value == 7

        rv = client.post(
            endpoint,
            json={
                "action": "save",
                "parent_id": parent_id,
                "child_id": child_id,
                "values": {
                    "id": str(child_id),
                    "name": "updated child",
                    "value": "8",
                },
            },
        )
        assert rv.status_code == 200

        with app.app_context():
            child = db.session.get(ModelC, child_id)
            assert child.name == "updated child"
            assert child.value == 8

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
            assert db.session.get(ModelC, child_id) is None

        rv = client.post(
            endpoint,
            json={
                "action": "delete",
                "parent_id": parent_id,
                "child_id": 999,
            },
        )
        assert rv.status_code == 404

    def test_ajax_one_to_one_inline_crud(
        self, app, client, admin, sqla_view_factory, login_as_admin
    ):
        """Test AJAX create/update/delete for a scalar inline relationship."""
        with app.app_context():
            db.reset_all()

            view = sqla_view_factory(
                OneToOneParent,
                endpoint="inline_o2o_delete",
                inline_models=(
                    InlineForm(
                        OneToOneChild,
                        inline_model_converter=InlineOneToOneModelConverter,
                    ),
                ),
            )
            admin.register_view(view)

            parent = OneToOneParent()
            child = OneToOneChild(test="existing", parent=parent)
            db.session.add(parent)
            db.session.commit()
            parent_id = parent.id
            child_id = child.id

            login_as_admin()

        edit_page = client.get(f"/admin/inline_o2o_delete/edit/?id={parent_id}")
        assert edit_page.status_code == 200
        assert "inline-model-row-template" in edit_page.get_data(as_text=True)

        rv = client.post(
            "/admin/inline_o2o_delete/ajax/inline/child/",
            json={
                "action": "save",
                "parent_id": parent_id,
                "child_id": child_id,
                "values": {"id": str(child_id), "test": "changed"},
            },
        )
        assert rv.status_code == 200

        with app.app_context():
            child = db.session.get(OneToOneChild, child_id)
            assert child.test == "changed"

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
            assert db.session.get(OneToOneChild, child_id) is None
            assert db.session.get(OneToOneParent, parent_id).child is None

    def test_inline_ajax_requires_csrf_token(
        self, app, client, admin, login_as_admin, sqla_view_factory
    ):
        """Inline AJAX mutations require the configured CSRF token."""
        app.config["CSRF_ENABLED"] = True
        with app.app_context():
            db.reset_all()

            view = sqla_view_factory(
                OneToManyParent,
                endpoint="inline_csrf",
                inline_models=(ManyToOneChild2,),
            )
            admin.register_view(view)
            parent = OneToManyParent()
            child = ManyToOneChild2(parent2=parent)
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
            "/admin/inline_csrf/ajax/inline/children2/",
            json={
                "action": "delete",
                "parent_id": parent_id,
                "child_id": child_id,
            },
        )
        assert rv.status_code == 400

        rv = client.post(
            "/admin/inline_csrf/ajax/inline/children2/",
            json={
                "action": "delete",
                "parent_id": parent_id,
                "child_id": child_id,
                "csrf_token": token,
            },
        )
        assert rv.status_code == 200

        with app.app_context():
            assert db.session.get(ManyToOneChild2, child_id) is None
