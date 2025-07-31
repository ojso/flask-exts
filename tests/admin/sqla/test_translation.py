from flask_babel import gettext
from flask_babel import force_locale
from flask_exts.admin.sqla import ModelView
from ...models import db, reset_models
from ...models.model1 import Model1
from .test_basic import CustomModelView


def test_column_label_translation(app, client, admin):
    with app.test_request_context():
        reset_models()

        with force_locale("zh"):
            label = gettext("Name")

        view = CustomModelView(
            Model1,
            column_list=["test1", "test3"],
            column_labels=dict(test1=label),
            column_filters=("test1",),
        )
        admin.add_view(view)

        rv = client.get("/admin/model1/?flt1_0=test")
        assert rv.status_code == 200
        # assert '{"Nombre":' in rv.text
        assert "名称" in rv.text


def test_unique_validator_translation_is_dynamic(app, client, admin):
    with app.app_context():

        class UniqueTable(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            value = db.Column(db.String, unique=True)

        db.create_all()

        view = ModelView(UniqueTable)
        view.can_create = True
        admin.add_view(view)

        rv = client.post(
            "/admin/uniquetable/new",
            data=dict(id="1", value="hello"),
            follow_redirects=True,
        )
        assert rv.status_code == 200

        rv = client.post(
            "/admin/uniquetable/new",
            data=dict(id="1", value="hello"),
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert "Already exists." in rv.text

        with force_locale("zh"):
            rv = client.post(
                "/admin/uniquetable/new",
                data=dict(id="1", value="hello"),
                follow_redirects=True,
            )
            assert rv.status_code == 200
            assert "已经存在" in rv.text
