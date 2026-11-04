from flask_babel import force_locale

from flask_exts.datastore.sqla import db

from .models.unique_validation import UniqueValidationModel


def test_unique_validator_translation_is_dynamic(
    app, client, admin, sqla_view_factory, login_as_admin
):
    with app.app_context():
        db.create_all()
        view = sqla_view_factory(
            UniqueValidationModel,
            name="test",
            endpoint="test",
        )
        admin.register_view(view)

        login_as_admin()

        rv = client.post(
            "/admin/test/new",
            data={"id": "1", "name": "test", "message": "hello"},
            follow_redirects=True,
        )
        assert rv.status_code == 200

        rv = client.post(
            "/admin/test/new",
            data={"id": "1", "name": "test", "message": "world"},
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert "Already exists." in rv.text

        with force_locale("zh"):
            rv = client.post(
                "/admin/test/new",
                data={"id": "1", "name": "test", "message": "world"},
                follow_redirects=True,
            )
            assert rv.status_code == 200
            assert "已经存在" in rv.text
