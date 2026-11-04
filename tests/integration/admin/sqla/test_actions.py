

from flask_exts.datastore.sqla import db
from flask_exts.datastore.sqla.query import Query

from .helpers import fill_admin_records
from .models.admin_records import AdminTestModel, RelatedAdminTestModel


def test_inline_column_editing(app, client, admin, sqla_view_factory, login_as_admin):
    with app.app_context():
        db.reset_all()

        view1 = sqla_view_factory(
            AdminTestModel, column_editable_list=["name", "enum_choice"]
        )
        admin.register_view(view1)
        # return
        # Test in-line editing for relations
        view2 = sqla_view_factory(
            RelatedAdminTestModel, column_editable_list=["admin_record"]
        )
        admin.register_view(view2)

        fill_admin_records()

        login_as_admin()

        # Test in-line edit field rendering
        rv = client.get("/admin/admintestmodel/")
        assert rv.status_code == 200
        assert "editable" in rv.text

        rv = client.get("/admin/relatedadmintestmodel/")
        assert rv.status_code == 200
        assert "editable" in rv.text

        # Form - Test basic in-line edit functionality
        rv = client.post(
            "/admin/admintestmodel/ajax/update/",
            json={
                "pk": "1",
                "name": "change-success-1",
            },
        )
        assert "Record was successfully saved." == rv.text

        # ensure the value has changed
        rv = client.get("/admin/admintestmodel/")
        assert "change-success-1" in rv.text

        # Test validation error
        rv = client.post(
            "/admin/admintestmodel/ajax/update/",
            json={
                "pk": "1",
                "enum_choice": "problematic-input",
            },
        )
        assert rv.status_code == 500

        # Test invalid primary key
        rv = client.post(
            "/admin/admintestmodel/ajax/update/",
            json={
                "pk": "1000",
                "name": "problematic-input",
            },
        )
        assert rv.status_code == 500

        # Test editing column not in column_editable_list
        rv = client.post(
            "/admin/admintestmodel/ajax/update/",
            json={
                "pk": "1",
                "description": "problematic-input",
            },
        )
        assert "problematic-input" not in rv.text

        rv = client.post(
            "/admin/relatedadmintestmodel/ajax/update/",
            json={
                "pk": "1",
                "admin_record": "3",
            },
        )
        assert "Record was successfully saved." == rv.text

        # confirm the value has changed
        rv = client.get("/admin/relatedadmintestmodel/")
        assert "test1_val_3" in rv.text


def test_bulk_delete_action(app, client, admin, sqla_view_factory, login_as_admin):
    with app.app_context():
        db.reset_all()

        db.session.add_all(
            [
                AdminTestModel(name="a"),
                AdminTestModel(name="b"),
                AdminTestModel(name="c"),
            ]
        )
        db.session.commit()
        query = Query(AdminTestModel)
        assert db.session.scalar(query.build_count()) == 3

        view = sqla_view_factory(AdminTestModel)
        admin.register_view(view)

        login_as_admin()

        rv = client.post(
            "/admin/admintestmodel/action/", data={"action": "delete", "rowid": [1, 2]}
        )
        assert rv.status_code == 302
        assert db.session.scalar(query.build_count()) == 1
