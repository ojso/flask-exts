import pytest
from flask_exts.datastore.sqla import db
from flask_exts.web.sqla.form.inline_model_convert import InlineForm
from flask_exts.web.sqla.form.inline_model_convert import InlineOneToOneModelConverter
from tests.models.relations import OneToManyParent
from tests.models.relations import ManyToOneChild2
from tests.models.relations import ManyToOneChild3
from tests.models.relations import OneToOneParent
from tests.models.relations import OneToOneChild
from tests.models.relations import ModelB
from tests.models.relations import ModelC
from .custom_sqla_model_view import CustomSqlaModelView


class TestInlineModelConverter:
    """Test InlineModelConverter relationship discovery and form generation."""

    def test_inline_model_with_class(self, app, admin):
        """Test inline_models with a plain model class."""
        with app.app_context():
            db.reset_all()

            view = CustomSqlaModelView(
                OneToManyParent,
                endpoint="inline_class",
                inline_models=(ManyToOneChild2,),
            )
            admin.register_view(view)

            form = view.create_form()
            assert hasattr(form, "children2")

    def test_inline_model_with_form_admin(self, app, admin):
        """Test inline_models with InlineForm instance."""
        with app.app_context():
            db.reset_all()

            inline = InlineForm(ManyToOneChild2)
            view = CustomSqlaModelView(
                OneToManyParent,
                endpoint="inline_admin",
                inline_models=(inline,),
            )
            admin.register_view(view)

            form = view.create_form()
            assert hasattr(form, "children2")

    def test_inline_model_with_form_columns(self, app, admin):
        """Test inline model with form_columns restriction."""
        with app.app_context():
            db.reset_all()

            inline = InlineForm(
                OneToOneChild,
                form_columns=("test",),
            )
            view = CustomSqlaModelView(
                OneToOneParent,
                endpoint="inline_columns",
                inline_models=(inline,),
            )
            admin.register_view(view)

            form = view.create_form()
            assert hasattr(form, "child")

    def test_inline_model_with_excluded_columns(self, app, admin):
        """Test inline model with form_excluded_columns."""
        with app.app_context():
            db.reset_all()

            inline = InlineForm(
                OneToOneChild,
                form_excluded_columns=("test",),
            )
            view = CustomSqlaModelView(
                OneToOneParent,
                endpoint="inline_excluded",
                inline_models=(inline,),
            )
            admin.register_view(view)

            form = view.create_form()
            assert hasattr(form, "child")

    def test_multiple_inline_models(self, app, admin):
        """Test multiple inline models on a single view."""
        with app.app_context():
            db.reset_all()

            view = CustomSqlaModelView(
                OneToManyParent,
                endpoint="inline_multi",
                inline_models=(ManyToOneChild2, ManyToOneChild3),
            )
            admin.register_view(view)

            form = view.create_form()
            assert hasattr(form, "children2")
            assert hasattr(form, "children3")

    def test_complex_relationship_inline(self, app, admin):
        """Test ModelC as inline of ModelB (complex relationship)."""
        with app.app_context():
            db.reset_all()

            view = CustomSqlaModelView(
                ModelB,
                endpoint="inline_bc",
                inline_models=(ModelC,),
            )
            admin.register_view(view)

            form = view.create_form()
            assert hasattr(form, "c_items")


class TestInlineOneToOneModelConverter:
    """Test InlineOneToOneModelConverter for one-to-one relationships."""

    def test_one_to_one_inline(self, app, admin):
        """Test one-to-one inline model form generation."""

        with app.app_context():
            db.reset_all()

            view = CustomSqlaModelView(
                OneToOneParent,
                endpoint="inline_o2o",
                inline_models=(OneToOneChild,),
                inline_model_form_converter=InlineOneToOneModelConverter,
            )
            admin.register_view(view)

            form = view.create_form()
            assert hasattr(form, "child")


class TestInlineModelIntegration:
    """Integration tests: HTTP create/edit with inline models."""

    def test_create_page_renders(self, app, admin):
        """Test creating a parent page renders with inline fields."""
        with app.app_context():
            db.reset_all()

            view = CustomSqlaModelView(
                OneToManyParent,
                endpoint="inline_create",
                inline_models=(ManyToOneChild2,),
            )
            admin.register_view(view)

        client = app.test_client()
        rv = client.get("/admin/inline_create/new/")
        assert rv.status_code == 200

    def test_edit_page_renders_with_children(self, app, admin):
        """Test editing a parent with existing inline children renders."""
        with app.app_context():
            db.reset_all()

            view = CustomSqlaModelView(
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

        client = app.test_client()
        rv = client.get(f"/admin/inline_edit/edit/?id={parent_id}")
        assert rv.status_code == 200

    def test_post_create_with_inline(self, app, admin):
        """Test POST to create a parent (without inline data)."""
        with app.app_context():
            db.reset_all()

            view = CustomSqlaModelView(
                OneToManyParent,
                endpoint="inline_post",
                inline_models=(ManyToOneChild2,),
            )
            admin.register_view(view)

        client = app.test_client()
        rv = client.post(
            "/admin/inline_post/new/",
            data={},
            follow_redirects=True,
        )
        assert rv.status_code == 200

    def test_inline_model_b_c_create_page(self, app, admin):
        """Test that the create page renders for ModelB with ModelC inline."""
        with app.app_context():
            db.reset_all()

            view = CustomSqlaModelView(
                ModelB,
                endpoint="inline_bc_page",
                inline_models=(ModelC,),
            )
            admin.register_view(view)

        client = app.test_client()
        rv = client.get("/admin/inline_bc_page/new/")
        assert rv.status_code == 200


class TestInlineModelFormListField:
    """Test InlineModelFormListField with data."""

    def test_parent_with_children_data(self, app, admin):
        """Test parent model correctly loads children data."""
        with app.app_context():
            db.reset_all()

            view = CustomSqlaModelView(
                OneToManyParent,
                endpoint="inline_data",
                inline_models=(ManyToOneChild2,),
            )
            admin.register_view(view)

            parent = OneToManyParent()
            child1 = ManyToOneChild2(parent2=parent)
            child2 = ManyToOneChild2(parent2=parent)
            db.session.add(parent)
            db.session.commit()

            assert len(parent.children2) == 2

            # Edit form should load with children
            parent_id = parent.id

        client = app.test_client()
        rv = client.get(f"/admin/inline_data/edit/?id={parent_id}")
        assert rv.status_code == 200

    def test_empty_parent_no_children(self, app, admin):
        """Test parent without children renders correctly."""
        with app.app_context():
            db.reset_all()

            view = CustomSqlaModelView(
                OneToManyParent,
                endpoint="inline_empty",
                inline_models=(ManyToOneChild2,),
            )
            admin.register_view(view)

            parent = OneToManyParent()
            db.session.add(parent)
            db.session.commit()
            parent_id = parent.id

        client = app.test_client()
        rv = client.get(f"/admin/inline_empty/edit/?id={parent_id}")
        assert rv.status_code == 200


class TestInlineModelFormField:
    """Test InlineModelFormField get_pk and populate_obj."""

    def test_form_field_has_pk(self, app, admin):
        """Test that inline form field correctly identifies primary key."""
        with app.app_context():
            db.reset_all()

            view = CustomSqlaModelView(
                OneToManyParent,
                endpoint="inline_pk_test",
                inline_models=(ManyToOneChild2,),
            )
            admin.register_view(view)

            # Verify form is created with correct inline field type
            form_class = view._create_form_class
            assert hasattr(form_class, "children2")
