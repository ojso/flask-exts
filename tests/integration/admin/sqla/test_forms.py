from wtforms import fields, validators

from flask_exts.datastore.sqla import db
from flask_exts.forms.fields import ChoiceField
from flask_exts.forms.form.base_form import BaseForm
from flask_exts.forms.widgets import TomSelectWidget

from .models.admin_records import AdminTestModel, RelatedAdminTestModel
from .models.form_views import AdminFormModel, RelatedAdminFormModel
from .models.one_to_one import OneToOneChildModel, OneToOneParentModel
from .models.string_fields import StringFieldModel


def test_form_extra_fields(app, client, admin, sqla_view_factory, login_as_admin):
    with app.app_context():
        db.reset_all()

        view = sqla_view_factory(
            AdminTestModel,
            form_extra_fields={"extra_field": fields.StringField("Extra Field")},
        )
        admin.register_view(view)

        login_as_admin()

        rv = client.get("/admin/admintestmodel/new/")
        assert rv.status_code == 200

        # Check presence and order
        assert "Extra Field" in rv.text
        pos1 = rv.text.find("Extra Field")
        pos2 = rv.text.find("Name")
        assert pos2 >= 0
        assert pos2 < pos1


def test_custom_form_base_class(app, admin, sqla_view_factory, login_as_admin):
    with app.app_context():

        class TestForm(BaseForm):
            pass

        db.reset_all()

        view = sqla_view_factory(AdminTestModel, base_form_class=TestForm)
        admin.register_view(view)

        create_form = view.create_form()
        assert isinstance(create_form, TestForm)


def test_model_required_fields(app, client, admin, sqla_view_factory, login_as_admin):
    with app.app_context():
        db.reset_all()

        class ModelView(sqla_view_factory):
            pass

        view = ModelView(RelatedAdminTestModel)
        admin.register_view(view)

        login_as_admin()

        rv = client.post("/admin/relatedadmintestmodel/new/", data={})
        assert "This field is required" in rv.text


STRING_CONSTANT = "Anyway, here's Wonderwall"


def test_nullable_and_required_string_fields(
    app, client, admin, sqla_view_factory, login_as_admin
):
    with app.app_context():
        db.create_all()

        view = sqla_view_factory(StringFieldModel)
        admin.register_view(view)

        login_as_admin()

        valid_params = {
            "case_number": 1,
            "required_string": STRING_CONSTANT,
            "required_text": STRING_CONSTANT,
        }
        rv = client.post("/admin/stringfieldmodel/new/", data=valid_params)
        assert rv.status_code == 302

        # Assert on defaults
        valid_inst = (
            db.session.query(StringFieldModel)
            .filter(StringFieldModel.case_number == 1)
            .one()
        )
        assert valid_inst.optional_string is None
        assert valid_inst.required_string == STRING_CONSTANT
        assert valid_inst.default_string == ""
        assert valid_inst.optional_text is None
        assert valid_inst.required_text == STRING_CONSTANT
        assert valid_inst.default_text == ""

        # Assert that nulls are caught on the non-null fields
        invalid_string_field = {
            "case_number": 2,
            "required_string": None,
            "required_text": STRING_CONSTANT,
        }
        rv = client.post("/admin/stringfieldmodel/new/", data=invalid_string_field)
        assert rv.status_code == 200
        assert "This field is required." in rv.text
        assert (
            db.session.query(StringFieldModel)
            .filter(StringFieldModel.case_number == 2)
            .all()
            == []
        )

        invalid_text_field = {
            "case_number": 3,
            "required_string": STRING_CONSTANT,
            "required_text": None,
        }
        rv = client.post("/admin/stringfieldmodel/new/", data=invalid_text_field)
        assert rv.status_code == 200
        assert "This field is required." in rv.text
        assert (
            db.session.query(StringFieldModel)
            .filter(StringFieldModel.case_number == 3)
            .all()
            == []
        )

        # Assert that empty strings are converted to None on nullable fields.
        empty_strings = {
            "case_number": 4,
            "optional_string": "",
            "optional_text": "",
            "required_string": STRING_CONSTANT,
            "required_text": STRING_CONSTANT,
        }
        rv = client.post("/admin/stringfieldmodel/new/", data=empty_strings)
        assert rv.status_code == 302
        empty_string_inst = (
            db.session.query(StringFieldModel)
            .filter(StringFieldModel.case_number == 4)
            .one()
        )
        assert empty_string_inst.optional_string is None
        assert empty_string_inst.optional_text is None


def test_form_column_selection(app, admin, sqla_view_factory):
    with app.app_context():
        db.reset_all()
        view1 = sqla_view_factory(
            AdminFormModel,
            endpoint="view1",
            form_columns=("integer_value", "text"),
        )

        view3 = sqla_view_factory(RelatedAdminFormModel, endpoint="view3")

        form1 = view1.create_form()
        form3 = view3.create_form()

        assert "integer_value" in form1._fields
        assert "text" in form1._fields
        assert "date_time" not in form1._fields

        # check that relation shows up as a query select
        assert type(form3.parent_form).__name__ == "QuerySelectField"

        # check that select field is rendered if form_choices were specified
        assert isinstance(form3.choice_value, ChoiceField)
        assert "<select " in str(form3.choice_value())
        assert "data-tom-select" not in str(form3.choice_value())
        assert 'data-tom-select="1"' in str(TomSelectWidget()(form3.choice_value))

        # check that select field is rendered for enum fields
        assert isinstance(form3.enum_choice, ChoiceField)

        # name form_columns with parent_form objects
        view4 = sqla_view_factory(
            AdminFormModel, endpoint="view1", form_columns=["integer_value"]
        )
        form4 = view4.create_form()
        assert "integer_value" in form4._fields


def test_form_field_validators(app, admin, sqla_view_factory):
    with app.app_context():
        db.reset_all()
        shared_form_args = {"name": {"validators": [validators.Regexp("name")]}}

        view = sqla_view_factory(AdminTestModel, form_args=shared_form_args)
        admin.register_view(view)

        create_form = view.create_form()
        # print(create_form.name.validators)
        assert len(create_form.name.validators) == 2

        # ensure shared field_args don't create duplicate validators
        edit_form = view.edit_form()
        assert len(edit_form.name.validators) == 2


def test_one_to_one_relationship_form(app, admin, sqla_view_factory):
    with app.app_context():
        db.reset_all()
        view1 = sqla_view_factory(OneToOneChildModel, endpoint="view1")
        view2 = sqla_view_factory(OneToOneParentModel, endpoint="view2")
        admin.register_view(view1)
        admin.register_view(view2)

        model1 = OneToOneChildModel(name="name")
        model2 = OneToOneParentModel(child=model1)
        db.session.add(model1)
        db.session.add(model2)
        db.session.commit()

        assert model1.parent == model2
        assert model2.child == model1

        assert not view1.create_form().parent.widget.multiple
        assert not view2.create_form().child.widget.multiple
