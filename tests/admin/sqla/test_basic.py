import pytest
from datetime import datetime, time, date
from wtforms import fields, validators
from flask_exts.template.form.base_form import BaseForm
from flask_exts.template.fields import Select2Field
from flask_exts.admin.sqla import ModelView, filters
from flask_exts.utils import sqla
from ...models import db, reset_models
from ...models.model1 import EnumChoices
from ...models.model1 import Model1, Model2, Model3
from ...models.model1 import ModelHybrid, ModelHybrid2
from ...models.model1 import ModelNoint
from ...models.model1 import ModelForm, ModelChild
from ...models.model1 import ModelMult
from ...models.model1 import ModelOnetoone1, ModelOnetoone2


class CustomModelView(ModelView):
    def __init__(
        self,
        model,
        name=None,
        endpoint=None,
        url=None,
        **kwargs,
    ):
        for k, v in kwargs.items():
            setattr(self, k, v)

        super().__init__(model, name=name, endpoint=endpoint, url=url)

    form_choices = {"choice_field": [("choice-1", "One"), ("choice-2", "Two")]}


def fill_db():
    model1_obj1 = Model1("test1_val_1", "test2_val_1", bool_field=True)
    model1_obj2 = Model1("test1_val_2", "test2_val_2", bool_field=False)
    model1_obj3 = Model1("test1_val_3", "test2_val_3")
    model1_obj4 = Model1("test1_val_4", "test2_val_4", choice_field="choice-1")

    model2_obj1 = Model2("test2_val_1", model1=model1_obj1, float_field=None)
    model2_obj2 = Model2("test2_val_2", model1=model1_obj2, float_field=None)
    model2_obj3 = Model2("test2_val_3", int_field=5000, float_field=25.9)
    model2_obj4 = Model2("test2_val_4", int_field=9000, float_field=75.5)
    model2_obj5 = Model2("test2_val_5", int_field=6169453081680413441)

    date_obj1 = Model1("date_obj1", date_field=date(2014, 11, 17))
    date_obj2 = Model1("date_obj2", date_field=date(2013, 10, 16))
    timeonly_obj1 = Model1("timeonly_obj1", time_field=time(11, 10, 9))
    timeonly_obj2 = Model1("timeonly_obj2", time_field=time(10, 9, 8))
    datetime_obj1 = Model1(
        "datetime_obj1", datetime_field=datetime(2014, 4, 3, 1, 9, 0)
    )
    datetime_obj2 = Model1(
        "datetime_obj2", datetime_field=datetime(2013, 3, 2, 0, 8, 0)
    )

    enum_obj1 = Model1("enum_obj1", enum_field="model1_v1")
    enum_obj2 = Model1("enum_obj2", enum_field="model1_v2")

    enum_type_obj1 = Model1("enum_type_obj1", enum_type_field=EnumChoices.first)
    enum_type_obj2 = Model1("enum_type_obj2", enum_type_field=EnumChoices.second)

    empty_obj = Model1(test2="empty_obj")

    db.session.add_all(
        [
            model1_obj1,
            model1_obj2,
            model1_obj3,
            model1_obj4,
            model2_obj1,
            model2_obj2,
            model2_obj3,
            model2_obj4,
            model2_obj5,
            date_obj1,
            timeonly_obj1,
            datetime_obj1,
            date_obj2,
            timeonly_obj2,
            datetime_obj2,
            enum_obj1,
            enum_obj2,
            enum_type_obj1,
            enum_type_obj2,
            empty_obj,
        ]
    )
    db.session.commit()


def test_model(app, client, admin):
    with app.app_context():
        reset_models()
        view = CustomModelView(Model1)
        admin.add_view(view)

        assert view.model == Model1
        assert view.name == "Model1"
        assert view.endpoint == "model1"

        assert view._primary_key == "id"

        assert "test1" in view._sortable_columns
        assert "test2" in view._sortable_columns
        assert "test3" in view._sortable_columns
        assert "test4" in view._sortable_columns

        assert view._create_form_class is not None
        assert view._edit_form_class is not None
        assert not view._search_supported
        assert view._filters is None

        # Verify form
        assert view._create_form_class.test1.field_class == fields.StringField
        assert view._create_form_class.test2.field_class == fields.StringField
        assert view._create_form_class.test3.field_class == fields.TextAreaField
        assert view._create_form_class.test4.field_class == fields.TextAreaField
        assert view._create_form_class.choice_field.field_class == Select2Field
        assert view._create_form_class.enum_field.field_class == Select2Field

        # check that we can retrieve a list view
        rv = client.get("/admin/model1/")
        assert rv.status_code == 200

        # check that we can retrieve a 'create' view
        rv = client.get("/admin/model1/new/")
        assert rv.status_code == 200

        # create a new record
        rv = client.post(
            "/admin/model1/new/",
            data=dict(
                test1="test1large",
                test2="test2",
                time_field=time(0, 0, 0),
                choice_field="choice-1",
                enum_field="model1_v1",
            ),
        )

        assert rv.status_code == 302

        # check that the new record was persisted
        model = db.session.query(Model1).first()
        assert model.test1 == "test1large"
        assert model.test2 == "test2"
        assert model.test3 == None
        assert model.test4 == None
        assert model.choice_field == "choice-1"
        assert model.enum_field == "model1_v1"

        # check that the new record shows up on the list view
        rv = client.get("/admin/model1/")
        assert rv.status_code == 200
        assert "test1large" in rv.text

        # check that we can retrieve an edit view
        url = "/admin/model1/edit/?id=%s" % model.id
        rv = client.get(url)
        assert rv.status_code == 200

        # verify that midnight does not show as blank
        assert "00:00:00" in rv.text

        # edit the record
        rv = client.post(
            url,
            data=dict(
                test1="test1small",
                test2="test2large",
                choice_field="__None",
                enum_field="__None",
            ),
        )
        assert rv.status_code == 302

        # check that the changes were persisted
        model = db.session.query(Model1).first()
        assert model.test1 == "test1small"
        assert model.test2 == "test2large"
        assert model.test3 == None
        assert model.test4 == None
        assert model.choice_field is None
        assert model.enum_field is None

        # check that the model can be deleted
        url = "/admin/model1/delete/?id=%s" % model.id
        rv = client.post(url)
        assert rv.status_code == 302
        assert db.session.query(Model1).count() == 0


@pytest.mark.xfail(raises=Exception)
def test_no_pk(admin):
    class Model(db.Model):
        test = db.Column(db.Integer)

    view = CustomModelView(Model)
    admin.add_view(view)


def test_list_columns(app, client, admin):
    with app.app_context():
        reset_models()

        # test column_list with a list of strings
        view1 = CustomModelView(
            Model1,
            name="view1",
            column_list=["test1", "test3"],
            column_labels=dict(test1="Column1"),
        )
        admin.add_view(view1)

        # test column_list with a list of SQLAlchemy columns
        view2 = CustomModelView(
            Model1,
            name="view2",
            endpoint="model1_2",
            column_list=[Model1.test1, Model1.test3],
            column_labels=dict(test1="Column1"),
        )
        admin.add_view(view2)

        assert len(view1._list_columns) == 2
        assert view1._list_columns == [("test1", "Column1"), ("test3", "Test3")]

        rv = client.get("/admin/model1/")
        assert "Column1" in rv.text
        assert "Test2" not in rv.text

        assert len(view2._list_columns) == 2
        assert view2._list_columns == [("test1", "Column1"), ("test3", "Test3")]

        rv = client.get("/admin/model1_2/")
        assert "Column1" in rv.text
        assert "Test2" not in rv.text


def test_complex_list_columns(app, client, admin):
    with app.app_context():
        reset_models()

        m1 = Model1("model1_val1")
        db.session.add(m1)
        db.session.add(Model2("model2_val1", model1=m1))

        db.session.commit()

        # test column_list with a list of strings on a relation
        view = CustomModelView(Model2, column_list=["model1.test1"])
        admin.add_view(view)

        rv = client.get("/admin/model2/")
        assert rv.status_code == 200
        assert "model1_val1" in rv.text


def test_exclude_columns(app, client, admin):
    with app.app_context():
        reset_models()
        view = CustomModelView(
            Model1,
            column_exclude_list=[
                "test2",
                "test4",
                "enum_field",
                "enum_type_field",
                "date_field",
                "datetime_field",
                "time_field",
            ],
        )
        admin.add_view(view)

        assert view._list_columns == [
            ("test1", "Test1"),
            ("test3", "Test3"),
            ("bool_field", "Bool Field"),
            ("email_field", "Email Field"),
            ("choice_field", "Choice Field"),
        ]

        rv = client.get("/admin/model1/")
        assert "Test1" in rv.text
        assert "Test2" not in rv.text


def test_column_searchable_list(app, client, admin):
    with app.app_context():
        reset_models()

        view = CustomModelView(
            Model2, column_searchable_list=["string_field", "int_field"]
        )
        admin.add_view(view)

        assert view._search_supported
        assert len(view._search_fields) == 2

        assert isinstance(view._search_fields[0][0], db.Column)
        assert isinstance(view._search_fields[1][0], db.Column)
        assert view._search_fields[0][0].name == "string_field"
        assert view._search_fields[1][0].name == "int_field"

        db.session.add(Model2("model1-test", 5000))
        db.session.add(Model2("model2-test", 9000))
        db.session.commit()

        rv = client.get("/admin/model2/?search=model1")
        assert "model1-test" in rv.text
        assert "model2-test" not in rv.text

        rv = client.get("/admin/model2/?search=9000")
        assert "model1-test" not in rv.text
        assert "model2-test" in rv.text


def test_extra_args_search(app, client, admin):
    with app.app_context():
        reset_models()
        view1 = CustomModelView(
            Model1,
            column_searchable_list=[
                "test1",
            ],
        )

        admin.add_view(view1)

        db.session.add(
            Model2(
                "model1-test",
            )
        )
        db.session.commit()

        # check that extra args in the url are propagated as hidden fields in the search form
        rv = client.get("/admin/model1/?search=model1&foo=bar")
        assert '<input type="hidden" name="foo" value="bar">' in rv.text


def test_extra_args_filter(app, client, admin):
    with app.app_context():
        reset_models()

        view2 = CustomModelView(
            Model2,
            column_filters=[
                "int_field",
            ],
        )
        admin.add_view(view2)

        db.session.add(Model2("model2-test", 5000))
        db.session.commit()

        # check that extra args in the url are propagated as hidden fields in the  form
        rv = client.get("/admin/model2/?flt1_0=5000&foo=bar")
        assert '<input type="hidden" name="foo" value="bar">' in rv.text



def test_complex_searchable_list(app, client, admin):
    with app.app_context():
        reset_models()

        view1 = CustomModelView(Model2, column_searchable_list=["model1.test1"])
        admin.add_view(view1)
        view2 = CustomModelView(Model1, column_searchable_list=[Model2.string_field])
        admin.add_view(view2)

        m1 = Model1("model1-test1-val")
        m2 = Model1("model1-test2-val")
        db.session.add(m1)
        db.session.add(m2)
        db.session.add(Model2("model2-test1-val", model1=m1))
        db.session.add(Model2("model2-test2-val", model1=m2))
        db.session.commit()

        # test relation string - 'model1.test1'
        rv = client.get("/admin/model2/?search=model1-test1")
        assert "model2-test1-val" in rv.text
        assert "model2-test2-val" not in rv.text

        # test relation object - Model2.string_field
        rv = client.get("/admin/model1/?search=model2-test1")
        assert "model1-test1-val" in rv.text
        assert "model1-test2-val" not in rv.text


def test_complex_searchable_list_missing_children(app, client, admin):
    with app.app_context():
        reset_models()

        view = CustomModelView(
            Model1, column_searchable_list=["test1", "model2.string_field"]
        )
        admin.add_view(view)

        db.session.add(Model1("magic string"))
        db.session.commit()

        rv = client.get("/admin/model1/?search=magic")
        assert "magic string" in rv.text



def test_column_editable_list(app, client, admin):
    with app.app_context():
        reset_models()

        view1 = CustomModelView(Model1, column_editable_list=["test1", "enum_field"])
        admin.add_view(view1)

        # Test in-line editing for relations
        view2 = CustomModelView(Model2, column_editable_list=["model1"])
        admin.add_view(view2)

        fill_db()

        # Test in-line edit field rendering
        rv = client.get("/admin/model1/")
        assert rv.status_code == 200
        assert 'data-role="x-editable"' in rv.text

        rv = client.get("/admin/model2/")
        assert rv.status_code == 200
        assert 'data-role="x-editable"' in rv.text
        assert 'data-role="x-editable"' in rv.text

        # Form - Test basic in-line edit functionality
        rv = client.post(
            "/admin/model1/ajax/update/",
            data={
                "list_form_pk": "1",
                "test1": "change-success-1",
            },
        )
        assert "Record was successfully saved." == rv.text

        # ensure the value has changed
        rv = client.get("/admin/model1/")
        assert "change-success-1" in rv.text

        # Test validation error
        rv = client.post(
            "/admin/model1/ajax/update/",
            data={
                "list_form_pk": "1",
                "enum_field": "problematic-input",
            },
        )
        assert rv.status_code == 500

        # Test invalid primary key
        rv = client.post(
            "/admin/model1/ajax/update/",
            data={
                "list_form_pk": "1000",
                "test1": "problematic-input",
            },
        )
        assert rv.status_code == 500

        # Test editing column not in column_editable_list
        rv = client.post(
            "/admin/model1/ajax/update/",
            data={
                "list_form_pk": "1",
                "test2": "problematic-input",
            },
        )
        assert "problematic-input" not in rv.text

        rv = client.post(
            "/admin/model2/ajax/update/",
            data={
                "list_form_pk": "1",
                "model1": "3",
            },
        )
        assert "Record was successfully saved." == rv.text

        # confirm the value has changed
        rv = client.get("/admin/model2/")
        assert "test1_val_3" in rv.text
 

def test_details_view(app, client, admin):
    with app.app_context():
        reset_models()

        view_no_details = CustomModelView(Model1, name="view1")
        admin.add_view(view_no_details)

        # fields are scaffolded
        view_w_details = CustomModelView(Model2, name="view2", can_view_details=True)
        admin.add_view(view_w_details)

        # show only specific fields in details w/ column_details_list
        string_field_view = CustomModelView(
            Model2,
            name="view3",
            can_view_details=True,
            column_details_list=["string_field"],
            endpoint="sf_view",
        )
        admin.add_view(string_field_view)

        fill_db()

        # ensure link to details is hidden when can_view_details is disabled
        rv = client.get("/admin/model1/")
        assert "/admin/model1/details/" not in rv.text

        # ensure link to details view appears
        rv = client.get("/admin/model2/")
        assert "/admin/model2/details/" in rv.text

        # test redirection when details are disabled
        rv = client.get("/admin/model1/details/?url=%2Fadmin%2Fmodel1%2F&id=1")
        assert rv.status_code == 302

        # test if correct data appears in details view when enabled
        rv = client.get("/admin/model2/details/?url=%2Fadmin%2Fmodel2%2F&id=1")
        assert "String Field" in rv.text
        assert "test2_val_1" in rv.text
        assert "test1_val_1" in rv.text

        # test column_details_list
        rv = client.get("/admin/sf_view/details/?url=%2Fadmin%2Fsf_view%2F&id=1")
        assert "String Field" in rv.text
        assert "test2_val_1" in rv.text
        assert "test1_val_1" not in rv.text


def test_editable_list_special_pks(app, client, admin):
    """Tests editable list view + a primary key with special characters"""
    with app.app_context():
        reset_models()
        view = CustomModelView(Model3, column_editable_list=["val1"])
        admin.add_view(view)

        db.session.add(Model3("1-1", "test1"))
        db.session.add(Model3("1-5", "test2"))
        db.session.commit()

        # Form - Test basic in-line edit functionality
        rv = client.post(
            "/admin/model3/ajax/update/",
            data={
                "list_form_pk": "1-1",
                "val1": "change-success-1",
            },
        )
        assert "Record was successfully saved." == rv.text

        # ensure the value has changed
        rv = client.get("/admin/model3/")
        assert "change-success-1" in rv.text


def test_column_filters(app, client, admin):
    with app.app_context():
        reset_models()

        view1 = CustomModelView(Model1, name="view1", column_filters=["test1"])
        admin.add_view(view1)

        assert len(view1._filters) == 7

        # Generate views
        view2 = CustomModelView(Model2, name="view2", column_filters=["model1"])

        view5 = CustomModelView(
            Model1, name="view5", column_filters=["test1"], endpoint="_strings"
        )
        admin.add_view(view5)

        view6 = CustomModelView(Model2, name="view6", column_filters=["int_field"])
        admin.add_view(view6)

        view7 = CustomModelView(
            Model1, name="view7", column_filters=["bool_field"], endpoint="_bools"
        )
        admin.add_view(view7)

        view8 = CustomModelView(
            Model2, name="view8", column_filters=["float_field"], endpoint="_float"
        )
        admin.add_view(view8)

        view9 = CustomModelView(
            Model2,
            name="view9",
            endpoint="_model2",
            column_filters=["model1.bool_field"],
            column_list=[
                "string_field",
                "model1.id",
                "model1.bool_field",
            ],
        )
        admin.add_view(view9)

        view10 = CustomModelView(
            Model1,
            name="view10",
            column_filters=["test1"],
            endpoint="_model3",
            named_filter_urls=True,
        )
        admin.add_view(view10)

        view11 = CustomModelView(
            Model1,
            name="view11",
            column_filters=["date_field", "datetime_field", "time_field"],
            endpoint="_datetime",
        )
        admin.add_view(view11)

        view12 = CustomModelView(
            Model1, name="view12", column_filters=["enum_field"], endpoint="_enumfield"
        )
        admin.add_view(view12)

        view13 = CustomModelView(
            Model2,
            name="view13",
            column_filters=[filters.FilterEqual(Model1.test1, "Test1")],
            endpoint="_relation_test",
        )
        admin.add_view(view13)

        view14 = CustomModelView(
            Model1,
            name="view14",
            column_filters=["enum_type_field"],
            endpoint="_enumtypefield",
        )
        admin.add_view(view14)

        # Test views
        assert [
            (f["index"], f["operation"]) for f in view1._filter_groups["Test1"]
        ] == [
            (0, "contains"),
            (1, "not contains"),
            (2, "equals"),
            (3, "not equal"),
            (4, "empty"),
            (5, "in list"),
            (6, "not in list"),
        ]

        # Test filter that references property0
        assert [
            (f["index"], f["operation"]) for f in view2._filter_groups["Model1 / Test1"]
        ] == [
            (0, "contains"),
            (1, "not contains"),
            (2, "equals"),
            (3, "not equal"),
            (4, "empty"),
            (5, "in list"),
            (6, "not in list"),
        ]

        assert [
            (f["index"], f["operation"]) for f in view2._filter_groups["Model1 / Test2"]
        ] == [
            (7, "contains"),
            (8, "not contains"),
            (9, "equals"),
            (10, "not equal"),
            (11, "empty"),
            (12, "in list"),
            (13, "not in list"),
        ]

        assert [
            (f["index"], f["operation"]) for f in view2._filter_groups["Model1 / Test3"]
        ] == [
            (14, "contains"),
            (15, "not contains"),
            (16, "equals"),
            (17, "not equal"),
            (18, "empty"),
            (19, "in list"),
            (20, "not in list"),
        ]

        assert [
            (f["index"], f["operation"]) for f in view2._filter_groups["Model1 / Test4"]
        ] == [
            (21, "contains"),
            (22, "not contains"),
            (23, "equals"),
            (24, "not equal"),
            (25, "empty"),
            (26, "in list"),
            (27, "not in list"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view2._filter_groups["Model1 / Bool Field"]
        ] == [
            (28, "equals"),
            (29, "not equal"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view2._filter_groups["Model1 / Date Field"]
        ] == [
            (30, "equals"),
            (31, "not equal"),
            (32, "greater than"),
            (33, "smaller than"),
            (34, "between"),
            (35, "not between"),
            (36, "empty"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view2._filter_groups["Model1 / Time Field"]
        ] == [
            (37, "equals"),
            (38, "not equal"),
            (39, "greater than"),
            (40, "smaller than"),
            (41, "between"),
            (42, "not between"),
            (43, "empty"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view2._filter_groups["Model1 / Datetime Field"]
        ] == [
            (44, "equals"),
            (45, "not equal"),
            (46, "greater than"),
            (47, "smaller than"),
            (48, "between"),
            (49, "not between"),
            (50, "empty"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view2._filter_groups["Model1 / Email Field"]
        ] == [
            (51, "contains"),
            (52, "not contains"),
            (53, "equals"),
            (54, "not equal"),
            (55, "empty"),
            (56, "in list"),
            (57, "not in list"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view2._filter_groups["Model1 / Enum Field"]
        ] == [
            (58, "equals"),
            (59, "not equal"),
            (60, "empty"),
            (61, "in list"),
            (62, "not in list"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view2._filter_groups["Model1 / Enum Type Field"]
        ] == [
            (63, "equals"),
            (64, "not equal"),
            (65, "empty"),
            (66, "in list"),
            (67, "not in list"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view2._filter_groups["Model1 / Choice Field"]
        ] == [
            (68, "contains"),
            (69, "not contains"),
            (70, "equals"),
            (71, "not equal"),
            (72, "empty"),
            (73, "in list"),
            (74, "not in list"),
        ]

        # Test filter with a dot
        view3 = CustomModelView(
            Model2, name="view3", column_filters=["model1.bool_field"]
        )

        assert [
            (f["index"], f["operation"])
            for f in view3._filter_groups["model1 / Model1 / Bool Field"]
        ] == [
            (0, "equals"),
            (1, "not equal"),
        ]

        # Test column_labels on filters
        view4 = CustomModelView(
            Model2,
            name="view4",
            column_filters=["model1.bool_field", "string_field"],
            column_labels={
                "model1.bool_field": "Test Filter #1",
                "string_field": "Test Filter #2",
            },
        )

        assert list(view4._filter_groups.keys()) == ["Test Filter #1", "Test Filter #2"]

        fill_db()

        # Test equals
        rv = client.get("/admin/model1/?flt0_0=test1_val_1")
        assert rv.status_code == 200
        # the filter value is always in "data"
        # need to check a different column than test1 for the expected row
        assert "test2_val_1" in rv.text
        assert "test1_val_2" not in rv.text

        # Test NOT IN filter
        rv = client.get("/admin/model1/?flt0_6=test1_val_1")
        assert rv.status_code == 200
        assert "test1_val_2" in rv.text
        assert "test2_val_1" not in rv.text

        # Test string filter
        assert [
            (f["index"], f["operation"]) for f in view5._filter_groups["Test1"]
        ] == [
            (0, "contains"),
            (1, "not contains"),
            (2, "equals"),
            (3, "not equal"),
            (4, "empty"),
            (5, "in list"),
            (6, "not in list"),
        ]

        # string - equals
        rv = client.get("/admin/_strings/?flt0_0=test1_val_1")
        assert rv.status_code == 200
        assert "test2_val_1" in rv.text
        assert "test1_val_2" not in rv.text

        # string - not equal
        rv = client.get("/admin/_strings/?flt0_1=test1_val_1")
        assert rv.status_code == 200
        assert "test2_val_1" not in rv.text
        assert "test1_val_2" in rv.text

        # string - contains
        rv = client.get("/admin/_strings/?flt0_2=test1_val_1")
        assert rv.status_code == 200
        assert "test2_val_1" in rv.text
        assert "test1_val_2" not in rv.text

        # string - not contains
        rv = client.get("/admin/_strings/?flt0_3=test1_val_1")
        assert rv.status_code == 200
        assert "test2_val_1" not in rv.text
        assert "test1_val_2" in rv.text

        # string - empty
        rv = client.get("/admin/_strings/?flt0_4=1")
        assert rv.status_code == 200
        assert "empty_obj" in rv.text
        assert "test1_val_1" not in rv.text
        assert "test1_val_2" not in rv.text

        # string - not empty
        rv = client.get("/admin/_strings/?flt0_4=0")
        assert rv.status_code == 200
        assert "empty_obj" not in rv.text
        assert "test1_val_1" in rv.text
        assert "test1_val_2" in rv.text

        # string - in list
        rv = client.get("/admin/_strings/?flt0_5=test1_val_1%2Ctest1_val_2")
        assert rv.status_code == 200
        assert "test2_val_1" in rv.text
        assert "test2_val_2" in rv.text
        assert "test1_val_3" not in rv.text
        assert "test1_val_4" not in rv.text

        # string - not in list
        rv = client.get("/admin/_strings/?flt0_6=test1_val_1%2Ctest1_val_2")
        assert rv.status_code == 200
        assert "test2_val_1" not in rv.text
        assert "test2_val_2" not in rv.text
        assert "test1_val_3" in rv.text
        assert "test1_val_4" in rv.text

        # Test integer filter
        assert [
            (f["index"], f["operation"]) for f in view6._filter_groups["Int Field"]
        ] == [
            (0, "equals"),
            (1, "not equal"),
            (2, "greater than"),
            (3, "smaller than"),
            (4, "empty"),
            (5, "in list"),
            (6, "not in list"),
        ]

        # integer - equals
        rv = client.get("/admin/model2/?flt0_0=5000")
        assert rv.status_code == 200
        assert "test2_val_3" in rv.text
        assert "test2_val_4" not in rv.text

        # integer - equals (huge number)
        rv = client.get("/admin/model2/?flt0_0=6169453081680413441")
        assert rv.status_code == 200
        assert "test2_val_5" in rv.text
        assert "test2_val_4" not in rv.text

        # integer - equals - test validation
        rv = client.get("/admin/model2/?flt0_0=badval")
        assert rv.status_code == 200
        assert "Invalid Filter Value" in rv.text

        # integer - not equal
        rv = client.get("/admin/model2/?flt0_1=5000")
        assert rv.status_code == 200
        assert "test2_val_3" not in rv.text
        assert "test2_val_4" in rv.text

        # integer - greater
        rv = client.get("/admin/model2/?flt0_2=6000")
        assert rv.status_code == 200
        assert "test2_val_3" not in rv.text
        assert "test2_val_4" in rv.text

        # integer - smaller
        rv = client.get("/admin/model2/?flt0_3=6000")
        assert rv.status_code == 200
        assert "test2_val_3" in rv.text
        assert "test2_val_4" not in rv.text

        # integer - empty
        rv = client.get("/admin/model2/?flt0_4=1")
        assert rv.status_code == 200
        assert "test2_val_1" in rv.text
        assert "test2_val_2" in rv.text
        assert "test2_val_3" not in rv.text
        assert "test2_val_4" not in rv.text

        # integer - not empty
        rv = client.get("/admin/model2/?flt0_4=0")
        assert rv.status_code == 200
        assert "test2_val_1" not in rv.text
        assert "test2_val_2" not in rv.text
        assert "test2_val_3" in rv.text
        assert "test2_val_4" in rv.text

        # integer - in list
        rv = client.get("/admin/model2/?flt0_5=5000%2C9000")
        assert rv.status_code == 200
        assert "test2_val_1" not in rv.text
        assert "test2_val_2" not in rv.text
        assert "test2_val_3" in rv.text
        assert "test2_val_4" in rv.text

        # integer - in list (huge number)
        rv = client.get("/admin/model2/?flt0_5=6169453081680413441")
        assert rv.status_code == 200
        assert "test2_val_1" not in rv.text
        assert "test2_val_5" in rv.text

        # integer - in list - test validation
        rv = client.get("/admin/model2/?flt0_5=5000%2Cbadval")
        assert rv.status_code == 200
        assert "Invalid Filter Value" in rv.text

        # integer - not in list
        rv = client.get("/admin/model2/?flt0_6=5000%2C9000")
        assert rv.status_code == 200
        assert "test2_val_1" in rv.text
        assert "test2_val_2" in rv.text
        assert "test2_val_3" not in rv.text
        assert "test2_val_4" not in rv.text

        # Test boolean filter
        assert [
            (f["index"], f["operation"]) for f in view7._filter_groups["Bool Field"]
        ] == [
            (0, "equals"),
            (1, "not equal"),
        ]

        # boolean - equals - Yes
        rv = client.get("/admin/_bools/?flt0_0=1")
        assert rv.status_code == 200
        assert "test2_val_1" in rv.text
        assert "test2_val_2" not in rv.text
        assert "test2_val_3" not in rv.text

        # boolean - equals - No
        rv = client.get("/admin/_bools/?flt0_0=0")
        assert rv.status_code == 200
        assert "test2_val_1" not in rv.text
        assert "test2_val_2" in rv.text
        assert "test2_val_3" in rv.text

        # boolean - not equals - Yes
        rv = client.get("/admin/_bools/?flt0_1=1")
        assert rv.status_code == 200
        assert "test2_val_1" not in rv.text
        assert "test2_val_2" in rv.text
        assert "test2_val_3" in rv.text

        # boolean - not equals - No
        rv = client.get("/admin/_bools/?flt0_1=0")
        assert rv.status_code == 200
        assert "test2_val_1" in rv.text
        assert "test2_val_2" not in rv.text
        assert "test2_val_3" not in rv.text

        # Test float filter
        assert [
            (f["index"], f["operation"]) for f in view8._filter_groups["Float Field"]
        ] == [
            (0, "equals"),
            (1, "not equal"),
            (2, "greater than"),
            (3, "smaller than"),
            (4, "empty"),
            (5, "in list"),
            (6, "not in list"),
        ]

        # float - equals
        rv = client.get("/admin/_float/?flt0_0=25.9")
        assert rv.status_code == 200
        assert "test2_val_3" in rv.text
        assert "test2_val_4" not in rv.text

        # float - equals - test validation
        rv = client.get("/admin/_float/?flt0_0=badval")
        assert rv.status_code == 200
        assert "Invalid Filter Value" in rv.text

        # float - not equal
        rv = client.get("/admin/_float/?flt0_1=25.9")
        assert rv.status_code == 200
        assert "test2_val_3" not in rv.text
        assert "test2_val_4" in rv.text

        # float - greater
        rv = client.get("/admin/_float/?flt0_2=60.5")
        assert rv.status_code == 200
        assert "test2_val_3" not in rv.text
        assert "test2_val_4" in rv.text

        # float - smaller
        rv = client.get("/admin/_float/?flt0_3=60.5")
        assert rv.status_code == 200
        assert "test2_val_3" in rv.text
        assert "test2_val_4" not in rv.text

        # float - empty
        rv = client.get("/admin/_float/?flt0_4=1")
        assert rv.status_code == 200
        assert "test2_val_1" in rv.text
        assert "test2_val_2" in rv.text
        assert "test2_val_3" not in rv.text
        assert "test2_val_4" not in rv.text

        # float - not empty
        rv = client.get("/admin/_float/?flt0_4=0")
        assert rv.status_code == 200
        assert "test2_val_1" not in rv.text
        assert "test2_val_2" not in rv.text
        assert "test2_val_3" in rv.text
        assert "test2_val_4" in rv.text

        # float - in list
        rv = client.get("/admin/_float/?flt0_5=25.9%2C75.5")
        assert rv.status_code == 200
        assert "test2_val_1" not in rv.text
        assert "test2_val_2" not in rv.text
        assert "test2_val_3" in rv.text
        assert "test2_val_4" in rv.text

        # float - in list - test validation
        rv = client.get("/admin/_float/?flt0_5=25.9%2Cbadval")
        assert rv.status_code == 200
        assert "Invalid Filter Value" in rv.text

        # float - not in list
        rv = client.get("/admin/_float/?flt0_6=25.9%2C75.5")
        assert rv.status_code == 200
        assert "test2_val_1" in rv.text
        assert "test2_val_2" in rv.text
        assert "test2_val_3" not in rv.text
        assert "test2_val_4" not in rv.text

        # Test filters to joined table field
        rv = client.get("/admin/_model2/?flt1_0=1")
        assert rv.status_code == 200
        assert "test2_val_1" in rv.text
        assert "test2_val_2" not in rv.text
        assert "test2_val_3" not in rv.text
        assert "test2_val_4" not in rv.text

        # Test human readable URLs
        rv = client.get("/admin/_model3/?flt1_test1_equals=test1_val_1")
        assert rv.status_code == 200
        assert "test1_val_1" in rv.text
        assert "test1_val_2" not in rv.text

        # Test date, time, and datetime filters
        assert [
            (f["index"], f["operation"]) for f in view11._filter_groups["Date Field"]
        ] == [
            (0, "equals"),
            (1, "not equal"),
            (2, "greater than"),
            (3, "smaller than"),
            (4, "between"),
            (5, "not between"),
            (6, "empty"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view11._filter_groups["Datetime Field"]
        ] == [
            (7, "equals"),
            (8, "not equal"),
            (9, "greater than"),
            (10, "smaller than"),
            (11, "between"),
            (12, "not between"),
            (13, "empty"),
        ]

        assert [
            (f["index"], f["operation"]) for f in view11._filter_groups["Time Field"]
        ] == [
            (14, "equals"),
            (15, "not equal"),
            (16, "greater than"),
            (17, "smaller than"),
            (18, "between"),
            (19, "not between"),
            (20, "empty"),
        ]

        # date - equals
        rv = client.get("/admin/_datetime/?flt0_0=2014-11-17")
        assert rv.status_code == 200
        assert "date_obj1" in rv.text
        assert "date_obj2" not in rv.text

        # date - not equal
        rv = client.get("/admin/_datetime/?flt0_1=2014-11-17")
        assert rv.status_code == 200
        assert "date_obj1" not in rv.text
        assert "date_obj2" in rv.text

        # date - greater
        rv = client.get("/admin/_datetime/?flt0_2=2014-11-16")
        assert rv.status_code == 200
        assert "date_obj1" in rv.text
        assert "date_obj2" not in rv.text

        # date - smaller
        rv = client.get("/admin/_datetime/?flt0_3=2014-11-16")
        assert rv.status_code == 200
        assert "date_obj1" not in rv.text
        assert "date_obj2" in rv.text

        # date - between
        rv = client.get("/admin/_datetime/?flt0_4=2014-11-13+-+2014-11-20")
        assert rv.status_code == 200
        assert "date_obj1" in rv.text
        assert "date_obj2" not in rv.text

        # date - not between
        rv = client.get("/admin/_datetime/?flt0_5=2014-11-13+-+2014-11-20")
        assert rv.status_code == 200
        assert "date_obj1" not in rv.text
        assert "date_obj2" in rv.text

        # date - empty
        rv = client.get("/admin/_datetime/?flt0_6=1")
        assert rv.status_code == 200
        assert "test1_val_1" in rv.text
        assert "date_obj1" not in rv.text
        assert "date_obj2" not in rv.text

        # date - empty
        rv = client.get("/admin/_datetime/?flt0_6=0")
        assert rv.status_code == 200
        assert "test1_val_1" not in rv.text
        assert "date_obj1" in rv.text
        assert "date_obj2" in rv.text

        # datetime - equals
        rv = client.get("/admin/_datetime/?flt0_7=2014-04-03+01%3A09%3A00")
        assert rv.status_code == 200
        assert "datetime_obj1" in rv.text
        assert "datetime_obj2" not in rv.text

        # datetime - not equal
        rv = client.get("/admin/_datetime/?flt0_8=2014-04-03+01%3A09%3A00")
        assert rv.status_code == 200
        assert "datetime_obj1" not in rv.text
        assert "datetime_obj2" in rv.text

        # datetime - greater
        rv = client.get("/admin/_datetime/?flt0_9=2014-04-03+01%3A08%3A00")
        assert rv.status_code == 200
        assert "datetime_obj1" in rv.text
        assert "datetime_obj2" not in rv.text

        # datetime - smaller
        rv = client.get("/admin/_datetime/?flt0_10=2014-04-03+01%3A08%3A00")
        assert rv.status_code == 200
        assert "datetime_obj1" not in rv.text
        assert "datetime_obj2" in rv.text

        # datetime - between
        rv = client.get(
            "/admin/_datetime/?flt0_11=2014-04-02+00%3A00%3A00+-+2014-11-20+23%3A59%3A59"
        )
        assert rv.status_code == 200
        assert "datetime_obj1" in rv.text
        assert "datetime_obj2" not in rv.text

        # datetime - not between
        rv = client.get(
            "/admin/_datetime/?flt0_12=2014-04-02+00%3A00%3A00+-+2014-11-20+23%3A59%3A59"
        )
        assert rv.status_code == 200
        assert "datetime_obj1" not in rv.text
        assert "datetime_obj2" in rv.text

        # datetime - empty
        rv = client.get("/admin/_datetime/?flt0_13=1")
        assert rv.status_code == 200
        assert "test1_val_1" in rv.text
        assert "datetime_obj1" not in rv.text
        assert "datetime_obj2" not in rv.text

        # datetime - not empty
        rv = client.get("/admin/_datetime/?flt0_13=0")
        assert rv.status_code == 200
        assert "test1_val_1" not in rv.text
        assert "datetime_obj1" in rv.text
        assert "datetime_obj2" in rv.text

        # time - equals
        rv = client.get("/admin/_datetime/?flt0_14=11%3A10%3A09")
        assert rv.status_code == 200
        assert "timeonly_obj1" in rv.text
        assert "timeonly_obj2" not in rv.text

        # time - not equal
        rv = client.get("/admin/_datetime/?flt0_15=11%3A10%3A09")
        assert rv.status_code == 200
        assert "timeonly_obj1" not in rv.text
        assert "timeonly_obj2" in rv.text

        # time - greater
        rv = client.get("/admin/_datetime/?flt0_16=11%3A09%3A09")
        assert rv.status_code == 200
        assert "timeonly_obj1" in rv.text
        assert "timeonly_obj2" not in rv.text

        # time - smaller
        rv = client.get("/admin/_datetime/?flt0_17=11%3A09%3A09")
        assert rv.status_code == 200
        assert "timeonly_obj1" not in rv.text
        assert "timeonly_obj2" in rv.text

        # time - between
        rv = client.get("/admin/_datetime/?flt0_18=10%3A40%3A00+-+11%3A50%3A59")
        assert rv.status_code == 200
        assert "timeonly_obj1" in rv.text
        assert "timeonly_obj2" not in rv.text

        # time - not between
        rv = client.get("/admin/_datetime/?flt0_19=10%3A40%3A00+-+11%3A50%3A59")
        assert rv.status_code == 200
        assert "timeonly_obj1" not in rv.text
        assert "timeonly_obj2" in rv.text

        # time - empty
        rv = client.get("/admin/_datetime/?flt0_20=1")
        assert rv.status_code == 200
        assert "test1_val_1" in rv.text
        assert "timeonly_obj1" not in rv.text
        assert "timeonly_obj2" not in rv.text

        # time - not empty
        rv = client.get("/admin/_datetime/?flt0_20=0")
        assert rv.status_code == 200
        assert "test1_val_1" not in rv.text
        assert "timeonly_obj1" in rv.text
        assert "timeonly_obj2" in rv.text

        # Test enum filter
        # enum - equals
        rv = client.get("/admin/_enumfield/?flt0_0=model1_v1")
        assert rv.status_code == 200
        assert "enum_obj1" in rv.text
        assert "enum_obj2" not in rv.text

        # enum - not equal
        rv = client.get("/admin/_enumfield/?flt0_1=model1_v1")
        assert rv.status_code == 200
        assert "enum_obj1" not in rv.text
        assert "enum_obj2" in rv.text

        # enum - empty
        rv = client.get("/admin/_enumfield/?flt0_2=1")
        assert rv.status_code == 200
        assert "test1_val_1" in rv.text
        assert "enum_obj1" not in rv.text
        assert "enum_obj2" not in rv.text

        # enum - not empty
        rv = client.get("/admin/_enumfield/?flt0_2=0")
        assert rv.status_code == 200
        assert "test1_val_1" not in rv.text
        assert "enum_obj1" in rv.text
        assert "enum_obj2" in rv.text

        # enum - in list
        rv = client.get("/admin/_enumfield/?flt0_3=model1_v1%2Cmodel1_v2")
        assert rv.status_code == 200
        assert "test1_val_1" not in rv.text
        assert "enum_obj1" in rv.text
        assert "enum_obj2" in rv.text

        # enum - not in list
        rv = client.get("/admin/_enumfield/?flt0_4=model1_v1%2Cmodel1_v2")
        assert rv.status_code == 200
        assert "test1_val_1" in rv.text
        assert "enum_obj1" not in rv.text
        assert "enum_obj2" not in rv.text

        # Test enum type filter
        # enum type - equals
        rv = client.get("/admin/_enumtypefield/?flt0_0=first")
        assert rv.status_code == 200
        assert "enum_type_obj1" in rv.text
        assert "enum_type_obj2" not in rv.text

        # enum - not equal
        rv = client.get("/admin/_enumtypefield/?flt0_1=first")
        assert rv.status_code == 200
        assert "enum_type_obj1" not in rv.text
        assert "enum_type_obj2" in rv.text

        # enum - empty
        rv = client.get("/admin/_enumtypefield/?flt0_2=1")
        assert rv.status_code == 200
        assert "test1_val_1" in rv.text
        assert "enum_type_obj1" not in rv.text
        assert "enum_type_obj2" not in rv.text

        # enum - not empty
        rv = client.get("/admin/_enumtypefield/?flt0_2=0")
        assert rv.status_code == 200
        assert "test1_val_1" not in rv.text
        assert "enum_type_obj1" in rv.text
        assert "enum_type_obj2" in rv.text

        # enum - in list
        rv = client.get("/admin/_enumtypefield/?flt0_3=first%2Csecond")
        assert rv.status_code == 200
        assert "test1_val_1" not in rv.text
        assert "enum_type_obj1" in rv.text
        assert "enum_type_obj2" in rv.text

        # enum - not in list
        rv = client.get("/admin/_enumtypefield/?flt0_4=first%2Csecond")
        assert rv.status_code == 200
        assert "test1_val_1" in rv.text
        assert "enum_type_obj1" not in rv.text
        assert "enum_type_obj2" not in rv.text

        # Test single custom filter on relation
        rv = client.get("/admin/_relation_test/?flt1_0=test1_val_1")
        assert "test1_val_1" in rv.text
        assert "test1_val_2" not in rv.text



def test_column_filters_sqla_obj(app, admin):
    with app.app_context():
        reset_models()

        view = CustomModelView(Model1, column_filters=[Model1.test1])
        admin.add_view(view)

        assert len(view._filters) == 7


def test_hybrid_property(app, client, admin):
    with app.app_context():
        reset_models()
        assert sqla.is_hybrid_property(ModelHybrid, "number_of_pixels")
        assert sqla.is_hybrid_property(ModelHybrid, "number_of_pixels_str")
        assert not sqla.is_hybrid_property(ModelHybrid, "height")
        assert not sqla.is_hybrid_property(ModelHybrid, "width")

        db.session.add(ModelHybrid(id=1, name="test_row_1", width=25, height=25))
        db.session.add(ModelHybrid(id=2, name="test_row_2", width=10, height=10))
        db.session.commit()

        view = CustomModelView(
            ModelHybrid,
            column_default_sort="number_of_pixels",
            column_filters=[
                filters.IntGreaterFilter(
                    ModelHybrid.number_of_pixels, "Number of Pixels"
                )
            ],
            column_searchable_list=[
                "number_of_pixels_str",
            ],
        )
        admin.add_view(view)

        # filters - hybrid_property integer - greater
        rv = client.get("/admin/modelhybrid/?flt0_0=600")
        assert rv.status_code == 200
        assert "test_row_1" in rv.text
        assert "test_row_2" not in rv.text

        # sorting
        rv = client.get("/admin/modelhybrid/?sort=0")
        assert rv.status_code == 200

        _, data = view.get_list(0, None, None, None, None)

        assert len(data) == 2
        assert data[0].name == "test_row_2"
        assert data[1].name == "test_row_1"

        # searching
        rv = client.get("/admin/modelhybrid/?search=100")
        assert rv.status_code == 200
        assert "test_row_2" in rv.text
        assert "test_row_1" not in rv.text



def test_hybrid_property_nested(app, client, admin):
    with app.app_context():
        reset_models()
        assert sqla.is_hybrid_property(ModelHybrid2, "owner.fullname")
        assert not sqla.is_hybrid_property(ModelHybrid2, "owner.firstname")

        db.session.add(ModelHybrid(id=1, firstname="John", lastname="Dow"))
        db.session.add(ModelHybrid(id=2, firstname="Jim", lastname="Smith"))
        db.session.add(ModelHybrid2(id=1, name="pencil", owner_id=1))
        db.session.add(ModelHybrid2(id=2, name="key", owner_id=1))
        db.session.add(ModelHybrid2(id=3, name="map", owner_id=2))
        db.session.commit()

        view = CustomModelView(
            ModelHybrid2,
            column_list=("id", "name", "owner.fullname"),
            column_default_sort="id",
        )
        admin.add_view(view)

        rv = client.get("/admin/modelhybrid2/")
        assert rv.status_code == 200
        assert "John Dow" in rv.text
        assert "Jim Smith" in rv.text


def test_url_args(app, client, admin):
    with app.app_context():
        reset_models()

        view = CustomModelView(
            Model1,
            page_size=2,
            column_searchable_list=["test1"],
            column_filters=["test1"],
        )
        admin.add_view(view)

        db.session.add(Model1("data1"))
        db.session.add(Model1("data2"))
        db.session.add(Model1("data3"))
        db.session.add(Model1("data4"))
        db.session.commit()

        rv = client.get("/admin/model1/")
        assert "data1" in rv.text
        assert "data3" not in rv.text

        # page
        rv = client.get("/admin/model1/?page=1")
        assert "data1" not in rv.text
        assert "data3" in rv.text

        # sort
        rv = client.get("/admin/model1/?sort=0&desc=1")
        assert "data1" not in rv.text
        assert "data3" in rv.text
        assert "data4" in rv.text

        # search
        rv = client.get("/admin/model1/?search=data1")
        assert "data1" in rv.text
        assert "data2" not in rv.text

        rv = client.get("/admin/model1/?search=^data1")
        assert "data2" not in rv.text

        # like
        rv = client.get("/admin/model1/?flt0=0&flt0v=data1")
        assert "data1" in rv.text

        # not like
        rv = client.get("/admin/model1/?flt0=1&flt0v=data1")
        assert "data2" in rv.text


def test_non_int_pk(app, client, admin):
    with app.app_context():
        reset_models()
        view = CustomModelView(ModelNoint, form_columns=["id", "test"])
        admin.add_view(view)

        rv = client.get("/admin/modelnoint/")
        assert rv.status_code == 200

        rv = client.post("/admin/modelnoint/new/", data=dict(id="test1", test="test2"))
        assert rv.status_code == 302

        rv = client.get("/admin/modelnoint/")
        assert rv.status_code == 200
        assert "test1" in rv.text

        rv = client.get("/admin/modelnoint/edit/?id=test1")
        assert rv.status_code == 200
        assert "test2" in rv.text


def test_form_columns(app, admin):
    with app.app_context():
        reset_models()
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
            ModelForm, endpoint="view1", form_columns=[ModelForm.int_field]
        )
        form4 = view4.create_form()
        assert "int_field" in form4._fields


@pytest.mark.xfail(raises=Exception)
def test_complex_form_columns(app, admin):
    with app.app_context():
        reset_models()

        # test using a form column in another table
        view = CustomModelView(Model2, form_columns=["model1.test1"])
        view.create_form()


def test_form_args(app, admin):
    with app.app_context():
        reset_models()
        shared_form_args = {"test1": {"validators": [validators.Regexp("test")]}}

        view = CustomModelView(Model1, form_args=shared_form_args)
        admin.add_view(view)

        create_form = view.create_form()
        # print(create_form.test1.validators)
        assert len(create_form.test1.validators) == 3

        # ensure shared field_args don't create duplicate validators
        edit_form = view.edit_form()
        assert len(edit_form.test1.validators) == 3


def test_form_override(app, admin):
    with app.app_context():
        reset_models()
        view1 = CustomModelView(Model1, name="view1", endpoint="view1")
        view2 = CustomModelView(
            Model1,
            name="view2",
            endpoint="view2",
            form_overrides=dict(test1=fields.FileField),
        )
        admin.add_view(view1)
        admin.add_view(view2)

        assert view1._create_form_class.test1.field_class == fields.StringField
        assert view2._create_form_class.test1.field_class == fields.FileField


def test_form_onetoone(app, admin):
    with app.app_context():
        reset_models()
        view1 = CustomModelView(ModelOnetoone1, endpoint="view1")
        view2 = CustomModelView(ModelOnetoone2, endpoint="view2")
        admin.add_view(view1)
        admin.add_view(view2)

        model1 = ModelOnetoone1(test="test")
        model2 = ModelOnetoone2(model1=model1)
        db.session.add(model1)
        db.session.add(model2)
        db.session.commit()

        assert model1.model2 == model2
        assert model2.model1 == model1

        assert not view1._create_form_class.model2.field_class.widget.multiple
        assert not view2._create_form_class.model1.field_class.widget.multiple


def test_relations():
    # TODO: test relations
    pass


def test_on_model_change_delete(app, client, admin):
    with app.app_context():
        reset_models()

        class ModelView(CustomModelView):
            def on_model_change(self, form, model, is_created):
                model.test1 = model.test1.upper()

            def on_model_delete(self, model):
                self.deleted = True

        view = ModelView(Model1)
        admin.add_view(view)

        client.post("/admin/model1/new/", data=dict(test1="test1large", test2="test2"))

        model = db.session.query(Model1).first()
        assert model.test1 == "TEST1LARGE"

        url = "/admin/model1/edit/?id=%s" % model.id
        client.post(url, data=dict(test1="test1small", test2="test2large"))

        model = db.session.query(Model1).first()
        assert model.test1 == "TEST1SMALL"

        url = "/admin/model1/delete/?id=%s" % model.id
        client.post(url)
        assert view.deleted


def test_multiple_delete(app, client, admin):
    with app.app_context():
        reset_models()

        db.session.add_all([Model1("a"), Model1("b"), Model1("c")])
        db.session.commit()
        assert Model1.query.count() == 3

        view = ModelView(Model1)
        admin.add_view(view)

        rv = client.post(
            "/admin/model1/action/", data=dict(action="delete", rowid=[1, 2, 3])
        )
        assert rv.status_code == 302
        assert Model1.query.count() == 0


def test_default_sort(app, admin):
    with app.app_context():
        reset_models()

        db.session.add_all([Model1("c", "x"), Model1("b", "x"), Model1("a", "y")])
        db.session.commit()
        assert Model1.query.count() == 3

        view1 = CustomModelView(Model1, name="view1", column_default_sort="test1")
        admin.add_view(view1)

        _, data = view1.get_list(0, None, None, None, None)

        assert len(data) == 3
        assert data[0].test1 == "a"
        assert data[1].test1 == "b"
        assert data[2].test1 == "c"

        # test default sort on renamed columns - with column_list scaffolding
        view2 = CustomModelView(
            Model1,
            name="view2",
            column_default_sort="test1",
            column_labels={"test1": "blah"},
            endpoint="m1_2",
        )
        admin.add_view(view2)

        _, data = view2.get_list(0, None, None, None, None)

        assert len(data) == 3
        assert data[0].test1 == "a"
        assert data[1].test1 == "b"
        assert data[2].test1 == "c"

        # test default sort on renamed columns - without column_list scaffolding
        view3 = CustomModelView(
            Model1,
            name="view3",
            column_default_sort="test1",
            column_labels={"test1": "blah"},
            endpoint="m1_3",
            column_list=["test1"],
        )
        admin.add_view(view3)

        _, data = view3.get_list(0, None, None, None, None)

        assert len(data) == 3
        assert data[0].test1 == "a"
        assert data[1].test1 == "b"
        assert data[2].test1 == "c"

        # test default sort with multiple columns
        order = [("test2", False), ("test1", False)]
        view4 = CustomModelView(Model1, column_default_sort=order, endpoint="m1_4")
        admin.add_view(view4)

        _, data = view4.get_list(0, None, None, None, None)

        assert len(data) == 3
        assert data[0].test1 == "b"
        assert data[1].test1 == "c"
        assert data[2].test1 == "a"


def test_complex_sort(app, client, admin):
    with app.app_context():
        reset_models()

        m1 = Model1(test1="c", test2="x")
        db.session.add(m1)
        db.session.add(Model2("c", model1=m1))

        m2 = Model1(test1="b", test2="x")
        db.session.add(m2)
        db.session.add(Model2("b", model1=m2))

        m3 = Model1(test1="a", test2="y")
        db.session.add(m3)
        db.session.add(Model2("a", model1=m3))

        db.session.commit()

        # test sorting on relation string - 'model1.test1'
        view1 = CustomModelView(
            Model2,
            name="view1",
            column_list=["string_field", "model1.test1"],
            column_sortable_list=["model1.test1"],
        )
        admin.add_view(view1)
        view2 = CustomModelView(
            Model2,
            name="view2",
            column_list=["string_field", "model1"],
            column_sortable_list=[("model1", ("model1.test2", "model1.test1"))],
            endpoint="m1_2",
        )
        admin.add_view(view2)

        rv = client.get("/admin/model2/?sort=0")
        assert rv.status_code == 200

        _, data = view1.get_list(0, "model1.test1", False, None, None)

        assert data[0].model1.test1 == "a"
        assert data[1].model1.test1 == "b"
        assert data[2].model1.test1 == "c"

        # test sorting on multiple columns in related model
        rv = client.get("/admin/m1_2/?sort=0")
        assert rv.status_code == 200

        _, data = view2.get_list(0, "model1", False, None, None)

        assert data[0].model1.test1 == "b"
        assert data[1].model1.test1 == "c"
        assert data[2].model1.test1 == "a"


@pytest.mark.xfail(raises=Exception)
def test_complex_sort_exception(app, admin):
    with app.app_context():
        reset_models()

        # test column_sortable_list on a related table's column object
        view = CustomModelView(
            Model2, endpoint="model2_3", column_sortable_list=[Model1.test1]
        )
        admin.add_view(view)

        sort_column = view._get_column_by_idx(0)[0]
        _, data = view.get_list(0, sort_column, False, None, None)

        assert len(data) == 2
        assert data[0].model1.test1 == "a"
        assert data[1].model1.test1 == "b"


def test_default_complex_sort(app, admin):
    with app.app_context():
        reset_models()

        m1 = Model1("b")
        db.session.add(m1)
        db.session.add(Model2("c", model1=m1))

        m2 = Model1("a")
        db.session.add(m2)
        db.session.add(Model2("c", model1=m2))

        db.session.commit()

        view1 = CustomModelView(
            Model2, name="view1", column_default_sort="model1.test1"
        )
        admin.add_view(view1)

        _, data = view1.get_list(0, None, None, None, None)

        assert len(data) == 2
        assert data[0].model1.test1 == "a"
        assert data[1].model1.test1 == "b"

        # test column_default_sort on a related table's column object
        view2 = CustomModelView(
            Model2,
            name="view2",
            endpoint="model2_2",
            column_default_sort=(Model1.test1, False),
        )
        admin.add_view(view2)

        _, data = view2.get_list(0, None, None, None, None)

        assert len(data) == 2
        assert data[0].model1.test1 == "a"
        assert data[1].model1.test1 == "b"


def test_extra_fields(app, client, admin):
    with app.app_context():
        reset_models()

        view = CustomModelView(
            Model1,
            form_extra_fields={"extra_field": fields.StringField("Extra Field")},
        )
        admin.add_view(view)

        rv = client.get("/admin/model1/new/")
        assert rv.status_code == 200

        # Check presence and order
        assert "Extra Field" in rv.text
        pos1 = rv.text.find("Extra Field")
        pos2 = rv.text.find("Test1")
        assert pos2 < pos1


def test_extra_field_order(app, client, admin):
    with app.app_context():
        reset_models()

        view = CustomModelView(
            Model1,
            form_columns=("extra_field", "test1"),
            form_extra_fields={"extra_field": fields.StringField("Extra Field")},
        )
        admin.add_view(view)

        rv = client.get("/admin/model1/new/")
        assert rv.status_code == 200

        # Check presence and order
        pos1 = rv.text.find("Extra Field")
        pos2 = rv.text.find("Test1")
        assert pos2 > pos1


def test_custom_form_base(app, admin):
    with app.app_context():

        class TestForm(BaseForm):
            pass

        reset_models()

        view = CustomModelView(Model1, form_base_class=TestForm)
        admin.add_view(view)

        assert hasattr(view._create_form_class, "test1")

        create_form = view.create_form()
        assert isinstance(create_form, TestForm)


def test_ajax_fk(app, client, admin):
    with app.app_context():
        reset_models()

        view = CustomModelView(
            Model2,
            url="view",
            form_ajax_refs={"model1": {"fields": ("test1", "test2")}},
        )
        admin.add_view(view)

        assert "model1" in view._form_ajax_refs

        model = Model1("first")
        model2 = Model1("foo", "bar")
        db.session.add_all([model, model2])
        db.session.commit()

        # Check loader
        loader = view._form_ajax_refs["model1"]
        mdl = loader.get_one(model.id)
        assert mdl.test1 == model.test1

        items = loader.get_list("fir")
        assert len(items) == 1
        assert items[0].id == model.id

        items = loader.get_list("bar")
        assert len(items) == 1
        assert items[0].test1 == "foo"

        # Check form generation
        form = view.create_form()
        assert form.model1.__class__.__name__ == "AjaxSelectField"

        with app.test_request_context("/admin/view/"):
            assert 'value=""' not in form.model1()

            form.model1.data = model
            # todo
            # assert (
            #     'data-json="[%s, &quot;first&quot;]"' % model.id in form.model1()
            #     or 'data-json="[%s, &#34;first&#34;]"' % model.id in form.model1()
            # )
            assert 'value="1"' in form.model1()

        # Check querying
        req = client.get("/admin/view/ajax/lookup/?name=model1&query=foo")
        # todo
        # assert req.data.decode("utf-8") == '[[%s, "foo"]]' % model2.id

        # Check submitting
        req = client.post("/admin/view/new/", data={"model1": str(model.id)})
        mdl = db.session.query(Model2).first()

        assert mdl is not None
        assert mdl.model1 is not None
        assert mdl.model1.id == model.id
        assert mdl.model1.test1 == "first"


def test_ajax_fk_multi(app, client, admin):
    with app.app_context():

        class Modelfk1(db.Model):
            __tablename__ = "modelfk1"

            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(20))

            def __str__(self):
                return self.name

        table = db.Table(
            "m2m",
            db.Model.metadata,
            db.Column("modelfk1_id", db.Integer, db.ForeignKey("modelfk1.id")),
            db.Column("modelfk2_id", db.Integer, db.ForeignKey("modelfk2.id")),
        )

        class Modelfk2(db.Model):
            __tablename__ = "modelfk2"

            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(20))

            modelfk1_id = db.Column(db.Integer(), db.ForeignKey(Modelfk1.id))
            modelfk1 = db.relationship(Modelfk1, backref="modelfks2", secondary=table)

        db.create_all()

        view = CustomModelView(
            Modelfk2,
            url="view",
            form_ajax_refs={"modelfk1": {"fields": ["name"]}},
        )
        admin.add_view(view)

        assert "modelfk1" in view._form_ajax_refs

        model = Modelfk1(name="first")
        db.session.add_all([model, Modelfk1(name="foo")])
        db.session.commit()

        # Check form generation
        form = view.create_form()
        assert form.modelfk1.__class__.__name__ == "AjaxSelectMultipleField"

        with app.test_request_context("/admin/view/"):
            assert 'data-json="[]"' in form.modelfk1()

            form.modelfk1.data = [model]
            # todo
            # assert (
            #     'data-json="[[1, &quot;first&quot;]]"' in form.model1()
            #     or 'data-json="[[1, &#34;first&#34;]]"' in form.model1()
            # )

        # Check submitting
        client.post("/admin/view/new/", data={"modelfk1": str(model.id)})
        mdl = db.session.query(Modelfk2).first()

        assert mdl is not None
        assert mdl.modelfk1 is not None
        assert len(mdl.modelfk1) == 1


def test_safe_redirect(app, client, admin):
    with app.app_context():
        reset_models()

        view = CustomModelView(Model1)
        admin.add_view(view)

        rv = client.post(
            "/admin/model1/new/?url=http://localhost/admin/model2view/",
            data=dict(
                test1="test1large",
                test2="test2",
                _continue_editing="Save and Continue Editing",
            ),
        )

        assert rv.status_code == 302

        # werkzeug 2.1.0+ now returns *relative* redirect/location by default.
        expected = "/admin/model1/edit/"

        # handle old werkzeug (or if relative location is disabled via `autocorrect_location_header=True`)
        if (
            not hasattr(rv, "autocorrect_location_header")
            or rv.autocorrect_location_header
        ):
            expected = "http://localhost" + expected

        assert rv.location.startswith(expected)
        assert "url=http://localhost/admin/model2view/" in rv.location
        assert "id=1" in rv.location

        rv = client.post(
            "/admin/model1/new/?url=http://google.com/evil/",
            data=dict(
                test1="test1large",
                test2="test2",
                _continue_editing="Save and Continue Editing",
            ),
        )

        assert rv.status_code == 302
        assert rv.location.startswith(expected)
        assert "url=/admin/model1/" in rv.location
        assert "id=2" in rv.location


def test_simple_list_pager(app, admin):
    with app.app_context():
        reset_models()

        class TestModelView(CustomModelView):
            simple_list_pager = True

            def get_count_query(self):
                assert False

        view = TestModelView(Model1)
        admin.add_view(view)

        count, data = view.get_list(0, None, None, None, None)
        assert count is None


def test_customising_page_size(app, client, admin):
    with app.app_context():
        reset_models()

        db.session.add_all([Model1(str(f"instance-{x+1:03d}")) for x in range(101)])

        view1 = CustomModelView(
            Model1,
            name="view1",
            endpoint="view1",
            page_size=20,
            can_set_page_size=False,
        )
        admin.add_view(view1)

        view2 = CustomModelView(
            Model1, name="view2", endpoint="view2", page_size=5, can_set_page_size=False
        )
        admin.add_view(view2)

        view3 = CustomModelView(
            Model1, name="view3", endpoint="view3", page_size=20, can_set_page_size=True
        )
        admin.add_view(view3)

        view4 = CustomModelView(
            Model1,
            name="view4",
            endpoint="view4",
            page_size=5,
            page_size_options=(5, 10, 15),
            can_set_page_size=True,
        )
        admin.add_view(view4)

        rv = client.get("/admin/view1/")
        assert "instance-020" in rv.text
        assert "instance-021" not in rv.text

        # `can_set_page_size=False`, so only the default of 20 is available.
        rv = client.get("/admin/view1/?page_size=50")
        assert "instance-020" in rv.text
        assert "instance-021" not in rv.text

        # Check view2, which has `page_size=5` to change the default page size
        rv = client.get("/admin/view2/")
        assert "instance-005" in rv.text
        assert "instance-006" not in rv.text

        # Check view3, which has `can_set_page_size=True`
        rv = client.get("/admin/view3/")
        assert "instance-020" in rv.text
        assert "instance-021" not in rv.text

        rv = client.get("/admin/view3/?page_size=50")
        assert "instance-050" in rv.text
        assert "instance-051" not in rv.text

        rv = client.get("/admin/view3/?page_size=100")
        assert "instance-100" in rv.text
        assert "instance-101" not in rv.text

        # Invalid page sizes are reset to the default
        rv = client.get("/admin/view3/?page_size=1")
        assert "instance-020" in rv.text
        assert "instance-021" not in rv.text

        # Check view4, which has custom `page_size_options`
        rv = client.get("/admin/view4/")
        assert "instance-005" in rv.text
        assert "instance-006" not in rv.text

        # Invalid page sizes are reset to the default
        rv = client.get("/admin/view4/?page_size=1")
        assert "instance-005" in rv.text
        assert "instance-006" not in rv.text

        rv = client.get("/admin/view4/?page_size=10")
        assert "instance-010" in rv.text
        assert "instance-011" not in rv.text

        rv = client.get("/admin/view4/?page_size=15")
        assert "instance-015" in rv.text
        assert "instance-016" not in rv.text


def test_unlimited_page_size(app, admin):
    with app.app_context():
        reset_models()

        db.session.add_all(
            [
                Model1("1"),
                Model1("2"),
                Model1("3"),
                Model1("4"),
                Model1("5"),
                Model1("6"),
                Model1("7"),
                Model1("8"),
                Model1("9"),
                Model1("10"),
                Model1("11"),
                Model1("12"),
                Model1("13"),
                Model1("14"),
                Model1("15"),
                Model1("16"),
                Model1("17"),
                Model1("18"),
                Model1("19"),
                Model1("20"),
                Model1("21"),
            ]
        )

        view = CustomModelView(Model1)

        # test 0 as page_size
        _, data = view.get_list(0, None, None, None, None, execute=True, page_size=0)
        assert len(data) == 21

        # test False as page_size
        _, data = view.get_list(
            0, None, None, None, None, execute=True, page_size=False
        )
        assert len(data) == 21


def test_advanced_joins(app, admin):
    with app.app_context():

        class Modeljoin1(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            val1 = db.Column(db.String(20))
            test = db.Column(db.String(20))

        class Modeljoin2(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            val2 = db.Column(db.String(20))

            model1_id = db.Column(db.Integer, db.ForeignKey(Modeljoin1.id))
            model1 = db.relationship(Modeljoin1, backref="model2")

        class Modeljoin3(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            val2 = db.Column(db.String(20))

            model2_id = db.Column(db.Integer, db.ForeignKey(Modeljoin2.id))
            model2 = db.relationship(Modeljoin2, backref="model3")

        view1 = CustomModelView(Modeljoin1)
        admin.add_view(view1)

        view2 = CustomModelView(Modeljoin2)
        admin.add_view(view2)

        view3 = CustomModelView(Modeljoin3)
        admin.add_view(view3)

        # Test joins
        attr, path = sqla.get_field_with_path(Modeljoin2, "model1.val1")
        assert attr == Modeljoin1.val1
        assert path == [Modeljoin2.model1]

        attr, path = sqla.get_field_with_path(Modeljoin1, "model2.val2")
        assert attr == Modeljoin2.val2
        assert id(path[0]) == id(Modeljoin1.model2)

        attr, path = sqla.get_field_with_path(Modeljoin3, "model2.model1.val1")
        assert attr == Modeljoin1.val1
        assert path == [Modeljoin3.model2, Modeljoin2.model1]

        # Test how joins are applied
        query = view3.get_query()

        joins = {}
        q1, joins, alias = view3._apply_path_joins(query, joins, path)
        assert (True, Modeljoin3.model2) in joins
        assert (True, Modeljoin2.model1) in joins
        assert alias is not None

        # Check if another join would use same path
        attr, path = sqla.get_field_with_path(Modeljoin2, "model1.test")
        q2, joins, alias = view2._apply_path_joins(query, joins, path)

        assert len(joins) == 2

        if hasattr(q2, "_join_entities"):
            for p in q2._join_entities:
                assert p in q1._join_entities

        assert alias is not None

        # Check if normal properties are supported by tools.get_field_with_path
        attr, path = sqla.get_field_with_path(Modeljoin2, Modeljoin1.test)
        assert attr == Modeljoin1.test
        assert path == [Modeljoin1.__table__]

        q3, joins, alias = view2._apply_path_joins(view2.get_query(), joins, path)
        assert len(joins) == 3
        assert alias is None


def test_multipath_joins(app, client, admin):
    with app.app_context():
        reset_models()
        view = CustomModelView(ModelMult, filters=["first.test"])
        admin.add_view(view)

        rv = client.get("/admin/modelmult/")
        assert rv.status_code == 200


def test_model_default(app, client, admin):
    with app.app_context():
        reset_models()

        class ModelView(CustomModelView):
            pass

        view = ModelView(Model2)
        admin.add_view(view)

        rv = client.post("/admin/model2/new/", data=dict())
        assert "This field is required" not in rv.text


def test_export_csv(app, client, admin):
    with app.app_context():
        reset_models()

        for x in range(5):
            fill_db()

        view1 = CustomModelView(
            Model1,
            name="view1",
            can_export=True,
            column_list=["test1", "test2"],
            export_max_rows=2,
            endpoint="row_limit_2",
        )
        admin.add_view(view1)
        view2 = CustomModelView(
            Model1,
            name="view2",
            can_export=True,
            column_list=["test1", "test2"],
            endpoint="no_row_limit",
        )
        admin.add_view(view2)

        # test export_max_rows
        rv = client.get("/admin/row_limit_2/export/csv/")
        assert rv.status_code == 200
        assert (
            "Test1,Test2\r\n"
            + "test1_val_1,test2_val_1\r\n"
            + "test1_val_2,test2_val_2\r\n"
            == rv.text
        )

        # test row limit without export_max_rows
        rv = client.get("/admin/no_row_limit/export/csv/")
        assert rv.status_code == 200
        assert len(rv.text.splitlines()) > 21


STRING_CONSTANT = "Anyway, here's Wonderwall"


def test_string_null_behavior(app, client, admin):
    with app.app_context():

        class StringTestModel(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            test_no = db.Column(db.Integer, nullable=False)
            string_field = db.Column(db.String)
            string_field_nonull = db.Column(db.String, nullable=False)
            string_field_nonull_default = db.Column(
                db.String, nullable=False, default=""
            )
            text_field = db.Column(db.Text)
            text_field_nonull = db.Column(db.Text, nullable=False)
            text_field_nonull_default = db.Column(db.Text, nullable=False, default="")

        db.create_all()

        view = CustomModelView(StringTestModel)
        admin.add_view(view)

        valid_params = {
            "test_no": 1,
            "string_field_nonull": STRING_CONSTANT,
            "text_field_nonull": STRING_CONSTANT,
        }
        rv = client.post("/admin/stringtestmodel/new/", data=valid_params)
        assert rv.status_code == 302

        # Assert on defaults
        valid_inst = (
            db.session.query(StringTestModel).filter(StringTestModel.test_no == 1).one()
        )
        assert valid_inst.string_field is None
        assert valid_inst.string_field_nonull == STRING_CONSTANT
        assert valid_inst.string_field_nonull_default == ""
        assert valid_inst.text_field is None
        assert valid_inst.text_field_nonull == STRING_CONSTANT
        assert valid_inst.text_field_nonull_default == ""

        # Assert that nulls are caught on the non-null fields
        invalid_string_field = {
            "test_no": 2,
            "string_field_nonull": None,
            "text_field_nonull": STRING_CONSTANT,
        }
        rv = client.post("/admin/stringtestmodel/new/", data=invalid_string_field)
        assert rv.status_code == 200
        assert "This field is required." in rv.text
        assert (
            db.session.query(StringTestModel).filter(StringTestModel.test_no == 2).all()
            == []
        )

        invalid_text_field = {
            "test_no": 3,
            "string_field_nonull": STRING_CONSTANT,
            "text_field_nonull": None,
        }
        rv = client.post("/admin/stringtestmodel/new/", data=invalid_text_field)
        assert rv.status_code == 200
        assert "This field is required." in rv.text
        assert (
            db.session.query(StringTestModel).filter(StringTestModel.test_no == 3).all()
            == []
        )

        # Assert that empty strings are converted to None on nullable fields.
        empty_strings = {
            "test_no": 4,
            "string_field": "",
            "text_field": "",
            "string_field_nonull": STRING_CONSTANT,
            "text_field_nonull": STRING_CONSTANT,
        }
        rv = client.post("/admin/stringtestmodel/new/", data=empty_strings)
        assert rv.status_code == 302
        empty_string_inst = (
            db.session.query(StringTestModel).filter(StringTestModel.test_no == 4).one()
        )
        assert empty_string_inst.string_field is None
        assert empty_string_inst.text_field is None
