import pytest
from wtforms import validators

from flask_exts.datastore.sqla import db
from flask_exts.forms.fields import ChoiceField
from flask_exts.forms.widgets import TomSelectWidget
from tests.models.demo import ChildModel, FormModel, Model1, Model2
from tests.models.relations import OneToOneChild, OneToOneParent

from .custom_sqla_model_view import CustomSqlaModelView


def test_form_columns(app, admin):
    with app.app_context():
        db.reset_all()
        view1 = CustomSqlaModelView(
            FormModel,
            endpoint="view1",
            form_columns=("int_field", "text_field"),
        )
        view2 = CustomSqlaModelView(
            FormModel,
            endpoint="view2",
            form_excluded_columns=("excluded_column",),
        )
        view3 = CustomSqlaModelView(ChildModel, endpoint="view3")

        form1 = view1.create_form()
        form2 = view2.create_form()
        form3 = view3.create_form()

        assert "int_field" in form1._fields
        assert "text_field" in form1._fields
        assert "datetime_field" not in form1._fields
        assert "excluded_column" not in form2._fields

        # check that relation shows up as a query select
        assert type(form3.model).__name__ == "QuerySelectField"

        # check that select field is rendered if form_choices were specified
        assert isinstance(form3.choice_field, ChoiceField)
        assert "<select " in str(form3.choice_field())
        assert "data-tom-select" not in str(form3.choice_field())
        assert 'data-tom-select="1"' in str(TomSelectWidget()(form3.choice_field))

        # check that select field is rendered for enum fields
        assert isinstance(form3.enum_field, ChoiceField)

        # test form_columns with model objects
        view4 = CustomSqlaModelView(
            FormModel, endpoint="view1", form_columns=["int_field"]
        )
        form4 = view4.create_form()
        assert "int_field" in form4._fields


@pytest.mark.xfail(raises=Exception)
def test_complex_form_columns(app, admin):
    with app.app_context():
        db.reset_all()

        # test using a form column in another table
        view = CustomSqlaModelView(Model2, form_columns=["model1.test1"])
        view.create_form()


def test_form_args(app, admin):
    with app.app_context():
        db.reset_all()
        shared_form_args = {"test1": {"validators": [validators.Regexp("test")]}}

        view = CustomSqlaModelView(Model1, form_args=shared_form_args)
        admin.register_view(view)

        create_form = view.create_form()
        # print(create_form.test1.validators)
        assert len(create_form.test1.validators) == 2

        # ensure shared field_args don't create duplicate validators
        edit_form = view.edit_form()
        assert len(edit_form.test1.validators) == 2


def test_form_onetoone(app, admin):
    with app.app_context():
        db.reset_all()
        view1 = CustomSqlaModelView(OneToOneChild, endpoint="view1")
        view2 = CustomSqlaModelView(OneToOneParent, endpoint="view2")
        admin.register_view(view1)
        admin.register_view(view2)

        model1 = OneToOneChild(test="test")
        model2 = OneToOneParent(child=model1)
        db.session.add(model1)
        db.session.add(model2)
        db.session.commit()

        assert model1.parent == model2
        assert model2.child == model1

        assert not view1._create_form_class.parent.field_class.widget.multiple
        assert not view2._create_form_class.child.field_class.widget.multiple
