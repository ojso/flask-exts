from flask_exts.datastore.sqla import db
from tests.models.multpk import Multpk
from flask_exts.admin.sqla.view import SqlaModelView
from .custom_sqla_model_view import CustomSqlaModelView


def test_multiple_pk(app, client, admin):
    with app.app_context():
        db.reset_all()
        view = CustomSqlaModelView(
            model=Multpk,
            endpoint="model",
            form_columns=["id", "id2", "data"],
        )
        admin.add_view(view)

        rv = client.get("/admin/model/")
        assert rv.status_code == 200

        rv = client.post("/admin/model/new/", data=dict(id=1, id2=2, data="test_multi"))
        assert rv.status_code == 302

        rv = client.get("/admin/model/")
        assert rv.status_code == 200
        assert "test_multi" in rv.text

        rv = client.get("/admin/model/edit/?id=1,2")
        assert rv.status_code == 200
        assert "test_multi" in rv.text

        rv = client.post(
            "/admin/model/edit/?id=1,2",
            data=dict(id=1, id2=2, data="test_multi_edited"),
        )
        assert rv.status_code == 302

        rv = client.get("/admin/model/details/?id=1,2")
        assert rv.status_code == 200
        assert "test_multi_edited" in rv.text
