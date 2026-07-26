from flask_babel import gettext
from flask_babel import force_locale
from flask_exts.admin.sqla.view import SqlaModelView
from flask_exts.datastore.sqla import db
from tests.models.model1 import Model1
from tests.models.unique import UniqueModel
from .test_basic import CustomSqlaModelView


def test_column_label_translation(app, client, admin):
    with app.test_request_context():
        db.reset_all()

        with force_locale("zh"):
            label = gettext("Name")

        view = CustomSqlaModelView(
            Model1,
            column_list=["test1", "test3"],
            column_labels=dict(test1=label),
            column_filters=("test1",),
        )
        admin.add_view(view)

        rv = client.get("/admin/model1/?flt1_0=test")
        assert rv.status_code == 200
        assert "名称" in rv.text


def test_unique_validator_translation_is_dynamic(app, client, admin):
    with app.app_context():
        db.create_all()
        view = SqlaModelView(UniqueModel)
        view.can_create = True
        admin.add_view(view)

        rv = client.post(
            "/admin/uniquemodel/new",
            data=dict(id="1", name="test", value="hello"),
            follow_redirects=True,
        )
        assert rv.status_code == 200

        rv = client.post(
            "/admin/uniquemodel/new",
            data=dict(id="1", name="test", value="world"),
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert "Already exists." in rv.text

        with force_locale("zh"):
            rv = client.post(
                "/admin/uniquemodel/new",
                data=dict(id="1", name="test", value="world"),
                follow_redirects=True,
            )
            assert rv.status_code == 200
            assert "已经存在" in rv.text
