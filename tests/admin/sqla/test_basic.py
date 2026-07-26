import pytest
from datetime import datetime, time, date
from wtforms import fields, validators
from flask_exts.template.forms.form.base_form import BaseForm
from flask_exts.template.forms.fields import Select2Field
from flask_exts.admin.sqla.view import SqlaModelView
from flask_exts.admin.sqla.query import Query
from flask_exts.datastore.sqla import db
from tests.models.model1 import EnumChoices
from tests.models.model1 import Model1, Model2
from .custom_sqla_model_view import CustomSqlaModelView

def fill_db():
    model1_obj1 = Model1(test1="test1_val_1", test2="test2_val_1", bool_field=True)
    model1_obj2 = Model1(test1="test1_val_2", test2="test2_val_2", bool_field=False)
    model1_obj3 = Model1(test1="test1_val_3", test2="test2_val_3")
    model1_obj4 = Model1(test1="test1_val_4", test2="test2_val_4", choice_field="choice-1")

    model2_obj1 = Model2(string_field="test2_val_1", model1=model1_obj1, float_field=None)
    model2_obj2 = Model2(string_field="test2_val_2", model1=model1_obj2, float_field=None)
    model2_obj3 = Model2(string_field="test2_val_3", int_field=5000, float_field=25.9)
    model2_obj4 = Model2(string_field="test2_val_4", int_field=9000, float_field=75.5)
    model2_obj5 = Model2(string_field="test2_val_5", int_field=6169453081680413441)

    date_obj1 = Model1(test1="date_obj1", date_field=date(2014, 11, 17))
    date_obj2 = Model1(test1="date_obj2", date_field=date(2013, 10, 16))
    timeonly_obj1 = Model1(test1="timeonly_obj1", time_field=time(11, 10, 9))
    timeonly_obj2 = Model1(test1="timeonly_obj2", time_field=time(10, 9, 8))
    datetime_obj1 = Model1(
        test1="datetime_obj1", datetime_field=datetime(2014, 4, 3, 1, 9, 0)
    )
    datetime_obj2 = Model1(
        test1="datetime_obj2", datetime_field=datetime(2013, 3, 2, 0, 8, 0)
    )

    enum_obj1 = Model1(test1="enum_obj1", enum_field="model1_v1")
    enum_obj2 = Model1(test1="enum_obj2", enum_field="model1_v2")

    enum_type_obj1 = Model1(test1="enum_type_obj1", enum_type_field=EnumChoices.first)
    enum_type_obj2 = Model1(test1="enum_type_obj2", enum_type_field=EnumChoices.second)

    empty_obj = Model1(test1="empty_obj")

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
        db.reset_all()
        view = CustomSqlaModelView(Model1)
        admin.add_view(view)

        assert view.model == Model1
        assert view.name == "Model1"
        assert view.endpoint == "model1"

        assert view._primary_key == "id"
        print(view._sortable_columns)
        return
        assert "test1" in view._sortable_columns
        assert "test2" in view._sortable_columns
        assert "test3" in view._sortable_columns
        assert "test4" in view._sortable_columns

        assert view._create_form_class is not None
        assert view._edit_form_class is not None
        assert len(view._filters) == 0

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
        assert model.string_field_optional == "test2"
        assert model.string_field_limit == None
        assert model.text_field == None
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
        assert model.string_field_optional == "test2large"
        assert model.string_field_limit == None
        assert model.text_field == None
        assert model.choice_field is None
        assert model.enum_field is None

        # check that the model can be deleted
        url = "/admin/model1/delete/"
        rv = client.post(url, data={"id": model.id})
        assert rv.status_code == 302
        assert db.session.query(Model1).count() == 0




def test_list_columns(app, client, admin):
    with app.app_context():
        db.reset_all()

        # test column_list with a list of strings
        view1 = CustomSqlaModelView(
            Model1,
            name="view1",
            column_list=["test1", "test3"],
            column_labels=dict(test1="Column1"),
        )
        admin.add_view(view1)

        # test column_list with a list of SQLAlchemy columns
        view2 = CustomSqlaModelView(
            Model1,
            name="view2",
            endpoint="model1_2",
            column_list=["test1", "test3"],
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
        db.reset_all()
        m1 = Model1(test1="model1_val1",test2="val2")
        db.session.add(m1)
        db.session.add(Model2(string_field="model2_val1", model1=m1))
        db.session.commit()

        # test column_list with a list of strings on a relation
        view = CustomSqlaModelView(Model2, column_list=["model1.test1"])
        admin.add_view(view)

        rv = client.get("/admin/model2/")
        assert rv.status_code == 200
        assert "model1_val1" in rv.text


def test_column_searchable_list(app, client, admin):
    with app.app_context():
        db.reset_all()

        view = CustomSqlaModelView(
            Model2, column_searchable_list=["string_field", "int_field"]
        )
        admin.add_view(view)

        db.session.add(Model2(string_field="model1-test", int_field=5000))
        db.session.add(Model2(string_field="model2-test", int_field=9000))
        db.session.commit()

        rv = client.get("/admin/model2/?search=model1")
        assert "model1-test" in rv.text
        assert "model2-test" not in rv.text

        rv = client.get("/admin/model2/?search=9000")
        assert "model1-test" not in rv.text
        assert "model2-test" in rv.text


def test_extra_args_search(app, client, admin):
    with app.app_context():
        db.reset_all()
        view1 = CustomSqlaModelView(
            Model1,
            column_searchable_list=[
                "test1",
            ],
        )

        admin.add_view(view1)

        db.session.add(Model2(string_field="model1-test",))
        db.session.commit()

        # check that extra args in the url are propagated as hidden fields in the search form
        rv = client.get("/admin/model1/?search=model1&foo=bar")
        assert '<input type="hidden" name="foo" value="bar">' in rv.text


def test_extra_args_filter(app, client, admin):
    with app.app_context():
        db.reset_all()

        view2 = CustomSqlaModelView(
            Model2,
            column_filters=[
                "int_field",
            ],
        )
        admin.add_view(view2)

        db.session.add(Model2(string_field="model2-test", int_field=5000))
        db.session.commit()

        # check that extra args in the url are propagated as hidden fields in the  form
        rv = client.get("/admin/model2/?flt1_0=5000&foo=bar")
        assert '<input type="hidden" name="foo" value="bar">' in rv.text


def test_complex_searchable_list(app, client, admin):
    with app.app_context():
        db.reset_all()

        view1 = CustomSqlaModelView(Model2, column_searchable_list=["model1.test1"])
        admin.add_view(view1)
        view2 = CustomSqlaModelView(Model1, column_searchable_list=["model2.string_field"])
        admin.add_view(view2)

        m1 = Model1(test1="model1-test1-val")
        m2 = Model1(test1="model1-test2-val")
        db.session.add(m1)
        db.session.add(m2)
        db.session.add(Model2(string_field="model2-test1-val", model1=m1))
        db.session.add(Model2(string_field="model2-test2-val", model1=m2))
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
        db.reset_all()

        view = CustomSqlaModelView(
            Model1, column_searchable_list=["test1", "model2.string_field"]
        )
        admin.add_view(view)

        db.session.add(Model1(test1="magic string"))
        db.session.commit()

        rv = client.get("/admin/model1/?search=magic")
        assert "magic string" in rv.text


def test_column_editable_list(app, client, admin):
    with app.app_context():
        db.reset_all()

        view1 = CustomSqlaModelView(Model1, column_editable_list=["test1", "enum_field"])
        admin.add_view(view1)

        # Test in-line editing for relations
        view2 = CustomSqlaModelView(Model2, column_editable_list=["model1"])
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
        db.reset_all()

        view_no_details = CustomSqlaModelView(Model1, name="view1")
        admin.add_view(view_no_details)

        # fields are scaffolded
        view_w_details = CustomSqlaModelView(Model2, name="view2")
        admin.add_view(view_w_details)

        # show only specific fields in details w/ column_details_list
        string_field_view = CustomSqlaModelView(
            Model2,
            name="view3",
            column_details_list=["string_field"],
            endpoint="sf_view",
        )
        admin.add_view(string_field_view)

        fill_db()

        # ensure link to details is hidden when can_view_details is disabled
        rv = client.get("/admin/model1/")
        assert "/admin/model1/details/" in rv.text

        # ensure link to details view appears
        rv = client.get("/admin/model2/")
        assert "/admin/model2/details/" in rv.text

        # test redirection when details are disabled
        rv = client.get("/admin/model1/details/?url=%2Fadmin%2Fmodel1%2F&id=1")
        assert rv.status_code == 200

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


def test_url_args(app, client, admin):
    with app.app_context():
        db.reset_all()

        view = CustomSqlaModelView(
            Model1,
            page_size=2,
            column_searchable_list=["test1"],
            column_filters=["test1"],
        )
        admin.add_view(view)

        db.session.add(Model1(test1="data1"))
        db.session.add(Model1(test1="data2"))
        db.session.add(Model1(test1="data3"))
        db.session.add(Model1(test1="data4"))
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




def test_relations():
    # TODO: test relations
    pass


def test_multiple_delete(app, client, admin):
    with app.app_context():
        db.reset_all()

        db.session.add_all([Model1(test1="a"), Model1(test1="b"), Model1(test1="c")])
        db.session.commit()
        query = Query(Model1)
        db.session.scalar(query.build_count()) ==3

        view = SqlaModelView(Model1)
        admin.add_view(view)

        rv = client.post(
            "/admin/model1/action/", data=dict(action="delete", rowid=[1, 2])
        )
        assert rv.status_code == 302
        db.session.scalar(query.build_count()) ==1


def test_default_sort(app, admin):
    with app.app_context():
        db.reset_all()

        db.session.add_all([Model1(test1="c", test2="x"), Model1(test1="b", test2="x"), Model1(test1="a", test2="y")])
        db.session.commit()
        query = Query(Model1)
        db.session.scalar(query.build_count()) ==3
        
        view1 = CustomSqlaModelView(Model1, name="view1", column_default_sort="test1")
        admin.add_view(view1)

        _, data = view1.get_list(0, None, None, None, None)

        assert len(data) == 3
        assert data[0].test1 == "a"
        assert data[1].test1 == "b"
        assert data[2].test1 == "c"

        # test default sort on renamed columns - with column_list scaffolding
        view2 = CustomSqlaModelView(
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
        view3 = CustomSqlaModelView(
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
        view4 = CustomSqlaModelView(Model1, column_default_sort=order, endpoint="m1_4")
        admin.add_view(view4)

        _, data = view4.get_list(0, None, None, None, None)

        assert len(data) == 3
        assert data[0].test1 == "b"
        assert data[1].test1 == "c"
        assert data[2].test1 == "a"


def test_complex_sort(app, client, admin):
    with app.app_context():
        db.reset_all()

        m1 = Model1(test1="c", test2="x")
        db.session.add(m1)
        db.session.add(Model2(string_field="c", model1=m1))

        m2 = Model1(test1="b", test2="x")
        db.session.add(m2)
        db.session.add(Model2(string_field="b", model1=m2))

        m3 = Model1(test1="a", test2="y")
        db.session.add(m3)
        db.session.add(Model2(string_field="a", model1=m3))

        db.session.commit()

        # test sorting on relation string - 'model1.test1'
        view1 = CustomSqlaModelView(
            Model2,
            name="view1",
            column_list=["string_field", "model1.test1"],
            column_sortable_list=["model1.test1"],
        )
        admin.add_view(view1)
        view2 = CustomSqlaModelView(
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
        db.reset_all()

        # test column_sortable_list on a related table's column object
        view = CustomSqlaModelView(
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
        db.reset_all()

        m1 = Model1(test1="b")
        db.session.add(m1)
        db.session.add(Model2(string_field="c", model1=m1))

        m2 = Model1(test1="a")
        db.session.add(m2)
        db.session.add(Model2(string_field="c", model1=m2))

        db.session.commit()

        view1 = CustomSqlaModelView(
            Model2, name="view1", column_default_sort="model1.test1"
        )
        admin.add_view(view1)

        _, data = view1.get_list(0, None, None, None, None)

        assert len(data) == 2
        assert data[0].model1.test1 == "a"
        assert data[1].model1.test1 == "b"

        # test column_default_sort on a related table's column object
        view2 = CustomSqlaModelView(
            Model2,
            name="view2",
            endpoint="model2_2",
            column_default_sort=("model1.test1", False),
        )
        admin.add_view(view2)

        _, data = view2.get_list(0, None, None, None, None)

        assert len(data) == 2
        assert data[0].model1.test1 == "a"
        assert data[1].model1.test1 == "b"


def test_extra_fields(app, client, admin):
    with app.app_context():
        db.reset_all()

        view = CustomSqlaModelView(
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
        db.reset_all()

        view = CustomSqlaModelView(
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

        db.reset_all()

        view = CustomSqlaModelView(Model1, form_base_class=TestForm)
        admin.add_view(view)

        assert hasattr(view._create_form_class, "test1")

        create_form = view.create_form()
        assert isinstance(create_form, TestForm)


def test_ajax_fk(app, client, admin):
    with app.app_context():
        db.reset_all()

        view = CustomSqlaModelView(
            Model2,
            url="view",
            form_ajax_refs={"model1": {"fields": ("test1", "test2")}},
        )
        admin.add_view(view)

        assert "model1" in view._form_ajax_refs

        model = Model1(test1="first")
        model2 = Model1(test1="foo", test2="bar")
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

        view = CustomSqlaModelView(
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


def test_customising_page_size(app, client, admin):
    with app.app_context():
        db.reset_all()

        db.session.add_all([Model1(test1=str(f"instance-{x+1:03d}")) for x in range(101)])

        view1 = CustomSqlaModelView(
            Model1,
            name="view1",
            endpoint="view1",
            page_size=20,
            can_set_page_size=False,
        )
        admin.add_view(view1)

        view2 = CustomSqlaModelView(
            Model1, name="view2", endpoint="view2", page_size=5, can_set_page_size=False
        )
        admin.add_view(view2)

        view3 = CustomSqlaModelView(
            Model1, name="view3", endpoint="view3", page_size=20, can_set_page_size=True
        )
        admin.add_view(view3)

        view4 = CustomSqlaModelView(
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
        db.reset_all()

        db.session.add_all(
            [
                Model1(test1="1"),
                Model1(test1="2"),
                Model1(test1="3"),
                Model1(test1="4"),
                Model1(test1="5"),
                Model1(test1="6"),
                Model1(test1="7"),
                Model1(test1="8"),
                Model1(test1="9"),
                Model1(test1="10"),
                Model1(test1="11"),
                Model1(test1="12"),
                Model1(test1="13"),
                Model1(test1="14"),
                Model1(test1="15"),
                Model1(test1="16"),
                Model1(test1="17"),
                Model1(test1="18"),
                Model1(test1="19"),
                Model1(test1="20"),
                Model1(test1="21"),
            ]
        )

        view = CustomSqlaModelView(Model1)

        # test 0 as page_size
        _, data = view.get_list(0, None, None, None, None, page_size=0)
        assert len(data) == 21

        # test False as page_size
        _, data = view.get_list(
            0, None, None, None, None, page_size=False
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

        view1 = CustomSqlaModelView(Modeljoin1)
        admin.add_view(view1)

        view2 = CustomSqlaModelView(Modeljoin2)
        admin.add_view(view2)

        view3 = CustomSqlaModelView(Modeljoin3)
        admin.add_view(view3)

        # Test how joins are applied
        query = view3.get_query()

        joins = {}
        q1, joins, alias = view3._apply_path_joins(query, joins, path)
        assert (True, Modeljoin3.model2) in joins
        assert (True, Modeljoin2.model1) in joins
        assert alias is not None

        # Check if another join would use same path
        attr, path = get_field_with_path(Modeljoin2, "model1.test")
        q2, joins, alias = view2._apply_path_joins(query, joins, path)

        assert len(joins) == 2

        if hasattr(q2, "_join_entities"):
            for p in q2._join_entities:
                assert p in q1._join_entities

        assert alias is not None

        # Check if normal properties are supported by get_field_with_path
        attr, path = get_field_with_path(Modeljoin2, "model1.test")
        assert attr == Modeljoin1.test
        assert path == [Modeljoin1.__table__]

        q3, joins, alias = view2._apply_path_joins(view2.get_query(), joins, path)
        assert len(joins) == 3
        assert alias is None


def test_model_default(app, client, admin):
    with app.app_context():
        db.reset_all()

        class ModelView(CustomSqlaModelView):
            pass

        view = ModelView(Model2)
        admin.add_view(view)

        rv = client.post("/admin/model2/new/", data=dict())
        assert "This field is required" in rv.text


def test_export_csv(app, client, admin):
    with app.app_context():
        db.reset_all()

        for x in range(5):
            fill_db()

        view1 = CustomSqlaModelView(
            Model1,
            name="view1",
            can_export=True,
            column_list=["test1", "test2"],
            export_max_rows=2,
            endpoint="row_limit_2",
        )
        admin.add_view(view1)
        view2 = CustomSqlaModelView(
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

        view = CustomSqlaModelView(StringTestModel)
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
