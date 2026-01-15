from flask_exts.datastore.sqla import db
from tests.datastore.sqla.models.model_multpk import ModelMultpk
from tests.datastore.sqla.models.polymorphic import Employee, ChildPoly, Manager
from tests.datastore.sqla.models.polymorphic import ChildCrete, ChildMultpk
from .test_basic import CustomModelView


def test_multiple_pk(app, client, admin):
    # Test multiple primary keys - mix int and string together
    with app.app_context():
        db.reset_models()
        view = CustomModelView(
            ModelMultpk,
            form_columns=["id", "id2", "data"],
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


def test_joined_inheritance(app, client, admin):
    # Test multiple primary keys - mix int and string together
    with app.app_context():
        db.reset_models()
        view = CustomModelView(
            ChildPoly, form_columns=["id", "test", "name"], endpoint="child"
        )
        admin.add_view(view)

        rv = client.get("/admin/child/")
        assert rv.status_code == 200

        rv = client.post("/admin/child/new/", data=dict(id=1, test="foo", name="bar"))
        assert rv.status_code == 302

        rv = client.get("/admin/child/edit/?id=1")
        assert rv.status_code == 200
        assert "foo" in rv.text
        assert "bar" in rv.text



def test_single_table_inheritance(app, client, admin):
    # Test multiple primary keys - mix int and string together
    with app.app_context():
        db.reset_models()

        view = CustomModelView(
            Manager,
            form_columns=["id", "test", "name"],
            endpoint="child",
        )
        admin.add_view(view)

        rv = client.get("/admin/child/")
        assert rv.status_code == 200

        rv = client.post("/admin/child/new/", data=dict(id=1, test="foo", name="bar"))
        assert rv.status_code == 302

        rv = client.get("/admin/child/edit/?id=1")
        assert rv.status_code == 200
        assert "foo" in rv.text
        assert "bar" in rv.text



def test_concrete_table_inheritance(app, client, admin):
    # Test multiple primary keys - mix int and string together
    with app.app_context():
        db.reset_models()
        view = CustomModelView(
            ChildCrete,
            form_columns=["id", "test", "name"],
            endpoint="child",
        )
        admin.add_view(view)

        rv = client.get("/admin/child/")
        assert rv.status_code == 200

        rv = client.post("/admin/child/new/", data=dict(id=1, test="foo", name="bar"))
        assert rv.status_code == 302

        rv = client.get("/admin/child/edit/?id=1")
        assert rv.status_code == 200
        assert "foo" in rv.text
        assert "bar" in rv.text



def test_concrete_multipk_inheritance(app, client, admin):
    # Test multiple primary keys - mix int and string together
    with app.app_context():
        db.reset_models()

        view = CustomModelView(
            ChildMultpk,
            form_columns=["id", "id2", "test", "name"],
            endpoint="child",
        )
        admin.add_view(view)

        rv = client.get("/admin/child/")
        assert rv.status_code == 200

        rv = client.post(
            "/admin/child/new/", data=dict(id=1, id2=2, test="foo", name="bar")
        )
        assert rv.status_code == 302

        rv = client.get("/admin/child/edit/?id=1,2")
        assert rv.status_code == 200
        assert "foo" in rv.text
        assert "bar" in rv.text
