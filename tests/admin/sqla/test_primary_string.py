from ...models import db
from .custom_sqla_model_view import CustomSqlaModelView
from ...models.primary_string_model import ModelPrimaryString

def test_non_int_pk(app, client, admin):
    with app.app_context():
        db.reset_all()
        view = CustomSqlaModelView(ModelPrimaryString, endpoint="model",form_columns=["id", "test"])
        admin.add_view(view)

        rv = client.get("/admin/model/")
        assert rv.status_code == 200

        rv = client.post("/admin/model/new/", data=dict(id="test1", test="test2"))
        assert rv.status_code == 302

        rv = client.get("/admin/model/")
        assert rv.status_code == 200
        assert "test1" in rv.text

        rv = client.get("/admin/model/edit/?id=test1")
        assert rv.status_code == 200
        assert "test2" in rv.text

