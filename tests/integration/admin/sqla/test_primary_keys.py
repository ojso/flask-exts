from flask_exts.datastore.sqla import db
from flask_exts.datastore.sqla.query import Query

from .models.composite_primary_key import CompositePrimaryKeyModel
from .models.primary_keys import StringPrimaryKeyModel


def test_string_primary_key(app, client, admin, sqla_view_factory, login_as_admin):
    with app.app_context():
        db.reset_all()
        view = sqla_view_factory(
            StringPrimaryKeyModel, endpoint="test", create_form_columns=["id", "value"]
        )
        admin.register_view(view)

        login_as_admin()

        rv = client.get("/admin/test/")
        assert rv.status_code == 200

        rv = client.post(
            "/admin/test/new/",
            data={"id": "test1", "value": "test2"},
            follow_redirects=True,
        )
        assert rv.status_code == 200

        rv = client.get("/admin/test/")
        assert rv.status_code == 200
        assert "test1" in rv.text
        assert "test2" in rv.text


def test_composite_primary_key(app, client, admin, sqla_view_factory, login_as_admin):

    with app.app_context():
        db.reset_all()
        view = sqla_view_factory(
            CompositePrimaryKeyModel,
            endpoint="test",
            create_form_columns=["id", "secondary_id", "payload"],
        )
        admin.register_view(view)

        login_as_admin()

        rv = client.get("/admin/test/")
        assert rv.status_code == 200

        rv = client.post(
            "/admin/test/new/",
            data={"id": 1, "secondary_id": 2, "payload": "test_multi"},
        )
        assert rv.status_code == 302

        rv = client.get("/admin/test/")
        assert rv.status_code == 200
        assert "test_multi" in rv.text

        rv = client.get("/admin/test/edit/?id=1,2")
        assert rv.status_code == 200
        assert "test_multi" in rv.text

        rv = client.post(
            "/admin/test/edit/?id=1,2",
            data={"id": 1, "secondary_id": 2, "payload": "test_multi_edited"},
        )
        assert rv.status_code == 302

        rv = client.get("/admin/test/details/?id=1,2")
        assert rv.status_code == 200
        assert "test_multi_edited" in rv.text


def test_bulk_delete_with_composite_primary_key(
    app, client, admin, sqla_view_factory, login_as_admin
):
    with app.app_context():
        db.reset_all()
        db.session.add_all(
            [
                CompositePrimaryKeyModel(id=1, secondary_id=1, payload="a"),
                CompositePrimaryKeyModel(id=1, secondary_id=2, payload="b"),
                CompositePrimaryKeyModel(id=2, secondary_id=1, payload="c"),
            ]
        )
        db.session.commit()
        query = Query(CompositePrimaryKeyModel)
        assert db.session.scalar(query.build_count()) == 3

        view = sqla_view_factory(
            CompositePrimaryKeyModel,
            endpoint="test",
            form_columns=["id", "secondary_id", "payload"],
        )
        admin.register_view(view)

        login_as_admin()

        rv = client.post(
            "/admin/test/action/", data={"action": "delete", "rowid": ["1, 1", "1, 2"]}
        )
        assert rv.status_code == 302
        assert db.session.scalar(query.build_count()) == 1
