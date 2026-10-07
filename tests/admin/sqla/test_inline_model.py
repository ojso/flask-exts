from flask_exts.admin.sqla.form.inline_model_convert import (
    InlineForm,
    InlineOneToOneModelConverter,
)
from flask_exts.datastore.sqla import db
from flask_exts.forms.fields.inline import InlineModelField
from flask_exts.forms.form.csrf import get_csrf_token
from tests.models.relations import (
    ManyToOneChild2,
    ManyToOneChild3,
    ModelB,
    ModelC,
    OneToManyParent,
    OneToOneChild,
    OneToOneParent,
)

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

    def test_inline_form_columns_retain_child_primary_key_field(self, app, admin):
        """Restricted inline forms retain their PK for identifying existing rows."""
        with app.app_context():
            db.reset_all()

            parent = OneToManyParent()
            child = ManyToOneChild2(parent2=parent)
            db.session.add(parent)
            db.session.commit()
            parent_id = parent.id

            view = CustomSqlaModelView(
                OneToManyParent,
                endpoint="inline_columns_pk",
                inline_models=(
                    InlineForm(ManyToOneChild2, form_columns=("parent_id",)),
                ),
            )
            admin.register_view(view)

            form = view.create_form(obj=parent)
            inline_field = form.children2
            assert "id" in inline_field.form_class()._fields
            assert inline_field.data == [child]

        rv = app.test_client().get(
            f"/admin/inline_columns_pk/edit/?id={parent_id}"
        )
        assert rv.status_code == 200
        assert 'name="children2-0-id"' in rv.get_data(as_text=True)

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
                inline_models=(
                    InlineForm(
                        OneToOneChild,
                        inline_model_converter=InlineOneToOneModelConverter,
                    ),
                ),
            )
            admin.register_view(view)

            form = view.create_form()
            assert hasattr(form, "child")
            assert isinstance(form.child, InlineModelField)
            assert not form.child.is_collection


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
        html = rv.get_data(as_text=True)
        assert "inline-model-row-template" in html
        assert "__prefix__-name" in html
        assert "js/form.js" in html
        assert "data-ajax-create-url" in html
        assert "data-parent-unsaved" in html

    def test_ajax_create_edit_and_delete_inline_rows(self, app, admin):
        """Test parent-first AJAX and independent inline row persistence."""
        with app.app_context():
            db.reset_all()

            view = CustomSqlaModelView(
                ModelB,
                endpoint="inline_crud",
                inline_models=(ModelC,),
            )
            admin.register_view(view)

        client = app.test_client()
        rv = client.post(
            "/admin/inline_crud/ajax/create-parent/",
            data={
                "name": "parent",
                "type": "kind",
            },
        )
        assert rv.status_code == 200
        parent_id = rv.json["id"]

        endpoint = "/admin/inline_crud/ajax/inline/c_items/"
        rv = client.post(
            endpoint,
            json={
                "action": "save",
                "parent_id": parent_id,
                "prefix": "c_items-0-",
                "values": {"id": "", "name": "first child", "value": "7"},
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
                "prefix": "c_items-0-",
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
                "prefix": "c_items-0-",
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
                "prefix": "c_items-0-",
            },
        )
        assert rv.status_code == 404

    def test_ajax_one_to_one_inline_crud(self, app, admin):
        """Test AJAX create/update/delete for a scalar inline relationship."""
        with app.app_context():
            db.reset_all()

            view = CustomSqlaModelView(
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

        client = app.test_client()
        edit_page = client.get(f"/admin/inline_o2o_delete/edit/?id={parent_id}")
        assert edit_page.status_code == 200
        assert "inline-model-row-template" in edit_page.get_data(as_text=True)

        rv = client.post(
            "/admin/inline_o2o_delete/ajax/inline/child/",
            json={
                "action": "save",
                "parent_id": parent_id,
                "child_id": child_id,
                "prefix": "child-0-",
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
                "prefix": "child-0-",
            },
        )
        assert rv.status_code == 200
        with app.app_context():
            assert db.session.get(OneToOneChild, child_id) is None
            assert db.session.get(OneToOneParent, parent_id).child is None

    def test_inline_ajax_requires_csrf_token(self, app, admin):
        """Inline AJAX mutations require the configured CSRF token."""
        app.config["CSRF_ENABLED"] = True
        with app.app_context():
            db.reset_all()
            view = CustomSqlaModelView(
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

        client = app.test_client()
        with client:
            rv = client.get(f"/admin/inline_csrf/edit/?id={parent_id}")
            assert rv.status_code == 200
            rv = client.post(
                "/admin/inline_csrf/ajax/inline/children2/",
                json={
                    "action": "delete",
                    "parent_id": parent_id,
                    "child_id": child_id,
                    "prefix": "children2-0-",
                },
            )
            assert rv.status_code == 400
            token = get_csrf_token()
            rv = client.post(
                "/admin/inline_csrf/ajax/inline/children2/",
                json={
                    "action": "delete",
                    "parent_id": parent_id,
                    "child_id": child_id,
                    "prefix": "children2-0-",
                    "csrf_token": token,
                },
            )
            assert rv.status_code == 200

        with app.app_context():
            assert db.session.get(ManyToOneChild2, child_id) is None
