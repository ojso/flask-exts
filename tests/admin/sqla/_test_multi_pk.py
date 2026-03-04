from flask_exts.datastore.sqla import db
from tests.datastore.sqla.models.multpk import Multpk
from flask_exts.admin.sqla.view import SqlaModelView


class CustomModelView(SqlaModelView):
    form_columns=["id", "id2", "data"],

def test_multiple_pk(app, client, admin):
    # Test multiple primary keys - mix int and string together
    with app.app_context():
        db.reset_all()
        view = CustomModelView(
            model=Multpk,            
            endpoint="model",
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

        # Correct order is mandatory -> fail here
        rv = client.get("/admin/model/edit/?id=2,1")
        assert rv.status_code == 302

