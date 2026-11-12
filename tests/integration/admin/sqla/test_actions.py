from datetime import datetime
from html.parser import HTMLParser

from flask_exts.datastore.sqla import db
from flask_exts.datastore.sqla.query import Query

from .helpers import fill_admin_records
from .models.admin_records import AdminTestModel, RelatedAdminTestModel


class EditableCellParser(HTMLParser):
    """Collect attributes from anchors rendered as inline-editable cells."""

    def __init__(self):
        super().__init__()
        self.cells = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attributes = dict(attrs)
        classes = (attributes.get("class") or "").split()
        if "editable" in classes:
            self.cells.append(attributes)


def test_column_editable_list_row_data(
    app, client, admin, sqla_view_factory, login_as_admin
):
    """Each editable cell must carry its own pk and displayed value."""
    with app.app_context():
        db.reset_all()

        datetime_obj1 = AdminTestModel(
            name="dt_obj1", datetime_value=datetime(2014, 4, 3, 1, 9, 0)
        )
        datetime_obj2 = AdminTestModel(
            name="dt_obj2", datetime_value=datetime(2013, 3, 2, 0, 8, 0)
        )
        db.session.add_all([datetime_obj1, datetime_obj2])
        db.session.commit()
        pk1, pk2 = datetime_obj1.id, datetime_obj2.id

        view = sqla_view_factory(
            AdminTestModel, column_editable_list=["datetime_value"]
        )
        admin.register_view(view)
        login_as_admin()

    rv = client.get("/admin/admintestmodel/")
    assert rv.status_code == 200

    parser = EditableCellParser()
    parser.feed(rv.text)
    datetime_cells = [
        cell for cell in parser.cells if cell.get("data-name") == "datetime_value"
    ]
    assert len(datetime_cells) == 2
    assert {cell["data-pk"]: cell["data-value"] for cell in datetime_cells} == {
        str(pk1): "2014-04-03 01:09:00",
        str(pk2): "2013-03-02 00:08:00",
    }


def test_ajax_update_requires_can_edit(
    app, client, admin, sqla_view_factory, login_as_admin
):
    with app.app_context():
        db.reset_all()

        view = sqla_view_factory(
            AdminTestModel, column_editable_list=["name"], can_edit=False
        )
        admin.register_view(view)

        db.session.add(AdminTestModel(name="original"))
        db.session.commit()

        login_as_admin()

        rv = client.post(
            "/admin/admintestmodel/ajax/update/",
            json={"pk": "1", "name": "changed"},
        )

        assert rv.status_code == 403
        assert db.session.get(AdminTestModel, 1).name == "original"


def test_inline_column_editing(app, client, admin, sqla_view_factory, login_as_admin):
    with app.app_context():
        db.reset_all()

        view1 = sqla_view_factory(
            AdminTestModel, column_editable_list=["name", "enum_choice"]
        )
        admin.register_view(view1)

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
