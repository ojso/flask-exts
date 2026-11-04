from flask_exts.admin.sqla.inline.inline_model_convert import InlineForm
from flask_exts.datastore.sqla import db
from flask_exts.forms.fields.inline import InlineModelField

from .models.multiple_foreign_keys import (
    MultipleForeignKeyChildModel,
    MultipleForeignKeyTargetModel,
)
from .models.one_to_many import (
    OneToManyBackPopulatedChildModel,
    OneToManyParentModel,
    OneToManySetChildModel,
)
from .models.one_to_one import OneToOneChildModel, OneToOneParentModel


class TestInlineModelConverter:
    """Test InlineModelConverter relationship discovery and form generation."""

    def test_inline_model_class_configuration(self, app, admin, sqla_view_factory):
        """Test inline_models with a plain model class."""
        with app.app_context():
            db.reset_all()

            view = sqla_view_factory(
                OneToManyParentModel,
                endpoint="inline_class",
                inline_models=(OneToManyBackPopulatedChildModel,),
            )
            admin.register_view(view)

            form = view.create_form()
            assert hasattr(form, "back_populated_children")

    def test_inline_model_form_configuration(self, app, admin, sqla_view_factory):
        """Test inline_models with InlineForm instance."""
        with app.app_context():
            db.reset_all()

            inline = InlineForm(OneToManyBackPopulatedChildModel)
            view = sqla_view_factory(
                OneToManyParentModel,
                endpoint="inline_admin",
                inline_models=(inline,),
            )
            admin.register_view(view)

            form = view.create_form()
            assert hasattr(form, "back_populated_children")

    def test_inline_form_column_selection(self, app, admin, sqla_view_factory):
        """Test inline model with form_columns restriction."""
        with app.app_context():
            db.reset_all()

            inline = InlineForm(
                OneToOneChildModel,
                form_columns=("name",),
            )
            view = sqla_view_factory(
                OneToOneParentModel,
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

            parent = OneToManyParentModel()
            child = OneToManyBackPopulatedChildModel(parent=parent)
            db.session.add(parent)
            db.session.commit()
            parent_id = parent.id

            view = sqla_view_factory(
                OneToManyParentModel,
                endpoint="inline_columns_pk",
                inline_models=(
                    InlineForm(
                        OneToManyBackPopulatedChildModel,
                        form_columns=(
                            "id",
                            "parent_id",
                        ),
                    ),
                ),
            )
            admin.register_view(view)

            form = view.edit_form(obj=parent)
            inline_field = form.back_populated_children
            assert "id" in inline_field.form_class()._fields
            assert inline_field.data == [child]

            login_as_admin()

        rv = client.get(f"/admin/inline_columns_pk/edit/?id={parent_id}")
        assert rv.status_code == 200
        assert 'name="back_populated_children-0-id"' in rv.get_data(as_text=True)

    def test_multiple_inline_relationships(self, app, admin, sqla_view_factory):
        """Test multiple inline models on a single view."""
        with app.app_context():
            db.reset_all()

            view = sqla_view_factory(
                OneToManyParentModel,
                endpoint="inline_multi",
                inline_models=(
                    OneToManyBackPopulatedChildModel,
                    OneToManySetChildModel,
                ),
            )
            admin.register_view(view)

            form = view.create_form()
            assert hasattr(form, "back_populated_children")
            assert hasattr(form, "set_children")

    def test_multiple_foreign_key_inline_relationship(
        self, app, admin, sqla_view_factory
    ):
        """Test the inline form for models with multiple foreign-key relationships."""
        with app.app_context():
            db.reset_all()

            view = sqla_view_factory(
                MultipleForeignKeyTargetModel,
                endpoint="inline_bc",
                inline_models=(MultipleForeignKeyChildModel,),
            )
            admin.register_view(view)

            form = view.edit_form()
            assert hasattr(form, "children")


class TestInlineOneToOneInlineModel:
    """Test InlineModelConverter for one-to-one relationships."""

    def test_one_to_one_inline_relationship(
        self, app, admin, client, login_as_admin, sqla_view_factory
    ):
        """Test one-to-one inline model form generation."""

        with app.app_context():
            db.reset_all()
            db.create_all()

            view = sqla_view_factory(
                OneToOneParentModel,
                endpoint="inline_o2o",
                inline_models=(InlineForm(OneToOneChildModel),),
            )
            admin.register_view(view)

            form = view.edit_form()
            assert hasattr(form, "child")
            assert isinstance(form.child, InlineModelField)
            assert not form.child.is_collection
