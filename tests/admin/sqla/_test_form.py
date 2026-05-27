import pytest
from tests.admin.sqla.models.model1 import ModelForm, ModelChild
from tests.admin.sqla.models.relations import OneToOneChild, OneToOneParent

def test_form_columns(app, admin):
    with app.app_context():
        db.reset_all()
        view1 = CustomModelView(
            ModelForm,
            endpoint="view1",
            form_columns=("int_field", "text_field"),
        )
        view2 = CustomModelView(
            ModelForm,
            endpoint="view2",
            form_excluded_columns=("excluded_column",),
        )
        view3 = CustomModelView(ModelChild, endpoint="view3")

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
        assert type(form3.choice_field).__name__ == "Select2Field"

        # check that select field is rendered for enum fields
        assert type(form3.enum_field).__name__ == "Select2Field"

        # test form_columns with model objects
        view4 = CustomModelView(
            ModelForm, endpoint="view1", form_columns=["int_field"]
        )
        form4 = view4.create_form()
        assert "int_field" in form4._fields


@pytest.mark.xfail(raises=Exception)
def test_complex_form_columns(app, admin):
    with app.app_context():
        db.reset_all()

        # test using a form column in another table
        view = CustomModelView(Model2, form_columns=["model1.test1"])
        view.create_form()


def test_form_args(app, admin):
    with app.app_context():
        db.reset_all()
        shared_form_args = {"test1": {"validators": [validators.Regexp("test")]}}

        view = CustomModelView(Model1, form_args=shared_form_args)
        admin.add_view(view)

        create_form = view.create_form()
        # print(create_form.test1.validators)
        assert len(create_form.test1.validators) == 2

        # ensure shared field_args don't create duplicate validators
        edit_form = view.edit_form()
        assert len(edit_form.test1.validators) == 2


def test_form_onetoone(app, admin):
    with app.app_context():
        db.reset_all()
        view1 = CustomModelView(OneToOneChild, endpoint="view1")
        view2 = CustomModelView(OneToOneParent, endpoint="view2")
        admin.add_view(view1)
        admin.add_view(view2)

        model1 = OneToOneChild(test="test")
        model2 = OneToOneParent(child=model1)
        db.session.add(model1)
        db.session.add(model2)
        db.session.commit()

        assert model1.parent == model2
        assert model2.child == model1

        assert not view1._create_form_class.parent.field_class.widget.multiple
        assert not view2._create_form_class.child.field_class.widget.multiple
        