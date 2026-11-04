from datetime import time

from wtforms import fields

from flask_exts.datastore.sqla import db
from flask_exts.forms.fields import ChoiceField

from .helpers import fill_admin_records
from .models.admin_records import AdminEnumChoice, AdminTestModel, RelatedAdminTestModel


def test_model_view_crud(app, client, admin, sqla_view_factory, login_as_admin):
    with app.app_context():
        db.reset_all()
        view = sqla_view_factory(AdminTestModel)
        admin.register_view(view)

        assert view.model == AdminTestModel
        assert view.name == "admintestmodel"
        assert view.endpoint == "admintestmodel"

        assert "name" in view._sortable_columns
        assert "description" in view._sortable_columns
        assert "short_text" in view._sortable_columns
        assert "long_text" in view._sortable_columns

        assert view._form_handler._create_form_class is not None
        assert view._form_handler._edit_form_class is not None
        assert len(view.get_filters()) == 0

        # Verify form
        assert (
            view._form_handler._create_form_class.name.field_class == fields.StringField
        )
        assert (
            view._form_handler._create_form_class.description.field_class
            == fields.StringField
        )
        assert (
            view._form_handler._create_form_class.short_text.field_class
            == fields.StringField
        )
        assert (
            view._form_handler._create_form_class.long_text.field_class
            == fields.TextAreaField
        )
        assert (
            view._form_handler._create_form_class.choice_value.field_class
            == ChoiceField
        )
        assert (
            view._form_handler._create_form_class.enum_choice.field_class == ChoiceField
        )

        login_as_admin()

        # check that we can retrieve a list view
        rv = client.get("/admin/admintestmodel/")
        assert rv.status_code == 200

        # check that we can retrieve a 'create' view
        rv = client.get("/admin/admintestmodel/new/")
        assert rv.status_code == 200

        # create a new record
        rv = client.post(
            "/admin/admintestmodel/new/",
            data={
                "name": "test1large",
                "description": "description",
                "time_value": time(0, 0, 0),
                "choice_value": "choice-1",
                "enum_choice": "first",
            },
        )
        assert rv.status_code == 302

        # check that the new record was persisted
        model = db.session.query(AdminTestModel).first()
        assert model.name == "test1large"
        assert model.description == "description"
        assert model.short_text is None
        assert model.long_text is None
        assert model.choice_value == "choice-1"
        assert model.enum_choice == AdminEnumChoice.first

        # check that the new record shows up on the list view
        rv = client.get("/admin/admintestmodel/")
        assert rv.status_code == 200
        assert "test1large" in rv.text

        # check that we can retrieve an edit view
        url = f"/admin/admintestmodel/edit/?id={model.id}"
        rv = client.get(url)
        assert rv.status_code == 200

        # verify that midnight does not show as blank
        assert "00:00:00" in rv.text

        # edit the record
        rv = client.post(
            url,
            data={
                "name": "test1small",
                "description": "test2large",
                "choice_value": "",
                "enum_choice": "",
            },
        )
        assert rv.status_code == 302

        # check that the changes were persisted
        model = db.session.query(AdminTestModel).first()
        assert model.name == "test1small"
        assert model.description == "test2large"
        assert model.short_text is None
        assert model.long_text is None
        assert model.choice_value is None
        assert model.enum_choice is None

        # check that the model can be deleted
        url = "/admin/admintestmodel/delete/"
        rv = client.post(url, data={"id": model.id})
        assert rv.status_code == 302
        assert db.session.query(AdminTestModel).count() == 0


def test_model_view_list_columns(app, client, admin, sqla_view_factory, login_as_admin):
    with app.app_context():
        db.reset_all()

        # test column_list with a list of strings
        view1 = sqla_view_factory(
            AdminTestModel,
            name="view1",
            column_list=["name", "short_text"],
            column_labels={"name": "Column1"},
        )
        admin.register_view(view1)

        # test column_list with a list of SQLAlchemy columns
        view2 = sqla_view_factory(
            AdminTestModel,
            name="view2",
            endpoint="model1_2",
            column_list=["name", "short_text"],
            column_labels={"name": "Column1"},
        )
        admin.register_view(view2)

        assert len(view1._list_columns) == 2
        assert view1._list_columns == [
            ("name", "Column1"),
            ("short_text", "Short Text"),
        ]

        login_as_admin()

        rv = client.get("/admin/admintestmodel/")
        assert "Column1" in rv.text
        assert "Description" not in rv.text

        assert len(view2._list_columns) == 2
        assert view2._list_columns == [
            ("name", "Column1"),
            ("short_text", "Short Text"),
        ]

        rv = client.get("/admin/model1_2/")
        assert "Column1" in rv.text
        assert "Description" not in rv.text


def test_related_model_view_list_columns(
    app, client, admin, sqla_view_factory, login_as_admin
):
    with app.app_context():
        db.reset_all()
        m1 = AdminTestModel(name="model1_val1", description="val2")
        db.session.add(m1)
        db.session.add(
            RelatedAdminTestModel(optional_string="model2_val1", admin_record=m1)
        )
        db.session.commit()

        # test column_list with a list of strings on a relation
        view = sqla_view_factory(
            RelatedAdminTestModel, column_list=["admin_record.name"]
        )
        admin.register_view(view)

        login_as_admin()

        rv = client.get("/admin/relatedadmintestmodel/")
        assert rv.status_code == 200
        assert "model1_val1" in rv.text


def test_model_view_details(app, client, admin, sqla_view_factory, login_as_admin):
    with app.app_context():
        db.reset_all()

        view_no_details = sqla_view_factory(AdminTestModel, name="view1")
        admin.register_view(view_no_details)

        # fields are scaffolded
        view_w_details = sqla_view_factory(RelatedAdminTestModel, name="view2")
        admin.register_view(view_w_details)

        # show only specific fields in details w/ column_details_list
        string_field_view = sqla_view_factory(
            RelatedAdminTestModel,
            name="view3",
            column_details_list=["optional_string"],
            endpoint="sf_view",
        )
        admin.register_view(string_field_view)

        fill_admin_records()

        login_as_admin()

        # ensure link to details is hidden when can_view_details is disabled
        rv = client.get("/admin/admintestmodel/")
        assert "/admin/admintestmodel/details/" in rv.text

        # ensure link to details view appears
        rv = client.get("/admin/relatedadmintestmodel/")
        assert "/admin/relatedadmintestmodel/details/" in rv.text

        # test redirection when details are disabled
        rv = client.get(
            "/admin/admintestmodel/details/?url=%2Fadmin%2Fadmintestmodel%2F&id=1"
        )
        assert rv.status_code == 200

        # test if correct data appears in details view when enabled
        rv = client.get(
            "/admin/relatedadmintestmodel/details/?url="
            "%2Fadmin%2Frelatedadmintestmodel%2F&id=1"
        )
        assert "Optional String" in rv.text
        assert "test2_val_1" in rv.text
        assert "test1_val_1" in rv.text

        # test column_details_list
        rv = client.get("/admin/sf_view/details/?url=%2Fadmin%2Fsf_view%2F&id=1")
        assert "Optional String" in rv.text
        assert "test2_val_1" in rv.text
        assert "test1_val_1" not in rv.text


def test_model_view_query_arguments(
    app, client, admin, sqla_view_factory, login_as_admin
):
    with app.app_context():
        db.reset_all()

        view = sqla_view_factory(
            AdminTestModel,
            page_size=2,
            column_searchable_list=["name"],
            column_filters=["name"],
        )
        admin.register_view(view)

        db.session.add(AdminTestModel(name="data1"))
        db.session.add(AdminTestModel(name="data2"))
        db.session.add(AdminTestModel(name="data3"))
        db.session.add(AdminTestModel(name="data4"))
        db.session.commit()

        login_as_admin()

        rv = client.get("/admin/admintestmodel/")
        assert "data1" in rv.text
        assert "data3" not in rv.text

        # page
        rv = client.get("/admin/admintestmodel/?page=1")
        assert "data1" not in rv.text
        assert "data3" in rv.text

        # sort
        rv = client.get("/admin/admintestmodel/?sort=0&desc=1")
        assert "data1" not in rv.text
        assert "data3" in rv.text
        assert "data4" in rv.text

        # search
        rv = client.get("/admin/admintestmodel/?search=data1")
        assert "data1" in rv.text
        assert "data2" not in rv.text

        rv = client.get("/admin/admintestmodel/?search=^data1")
        assert "data2" not in rv.text

        # like
        rv = client.get("/admin/admintestmodel/?flt0=0&flt0v=data1")
        assert "data1" in rv.text

        # not like
        rv = client.get("/admin/admintestmodel/?flt0=1&flt0v=data1")
        assert "data2" in rv.text
