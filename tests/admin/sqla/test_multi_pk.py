from flask_exts.admin.sqla.view import SqlaModelView
from flask_exts.datastore.sqla import db
from flask_exts.datastore.sqla.query import Query
from tests.models.multpk import Multpk

from .custom_sqla_model_view import CustomSqlaModelView


def test_multiple_pk(app, client, admin):
    with app.app_context():
        db.reset_all()
        view = CustomSqlaModelView(
            model=Multpk,
            endpoint="model",
            form_columns=["id", "id2", "data"],
        )
        admin.register_view(view)

        rv = client.get("/admin/model/")
        assert rv.status_code == 200

        rv = client.post(
            "/admin/model/new/", data={"id": 1, "id2": 2, "data": "test_multi"}
        )
        assert rv.status_code == 302

        rv = client.get("/admin/model/")
        assert rv.status_code == 200
        assert "test_multi" in rv.text

        rv = client.get("/admin/model/edit/?id=1,2")
        assert rv.status_code == 200
        assert "test_multi" in rv.text

        rv = client.post(
            "/admin/model/edit/?id=1,2",
            data={"id": 1, "id2": 2, "data": "test_multi_edited"},
        )
        assert rv.status_code == 302

        rv = client.get("/admin/model/details/?id=1,2")
        assert rv.status_code == 200
        assert "test_multi_edited" in rv.text


def test_multiple_pk_delete(app, client, admin):
    with app.app_context():
        db.reset_all()

        db.session.add_all([Multpk(id=1,id2=1,data="a"), Multpk(id=1,id2=2,data="b"), Multpk(id=2,id2=1,data="c")])
        db.session.commit()
        query = Query(Multpk)
        assert db.session.scalar(query.build_count()) == 3

        view = CustomSqlaModelView(
            model=Multpk,
            endpoint="model",
            form_columns=["id", "id2", "data"],
        )
        admin.register_view(view)

        rv = client.post(
            "/admin/model/action/", data={"action": "delete", "rowid": ["1, 1","1, 2"]}
        )
        assert rv.status_code == 302
        assert db.session.scalar(query.build_count()) == 1
