from flask_babel import force_locale
from sqlalchemy.orm import Mapped, mapped_column

from flask_exts.datastore.sqla import db


class UniqueModel(db.Model):
    __tablename__ = "unique"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    value: Mapped[str]


def test_unique_validator_translation_is_dynamic(
    app, client, admin, sqla_view_factory, login_as_admin
):
    with app.app_context():
        db.create_all()
        view = sqla_view_factory(
            UniqueModel,
            name="test",
            endpoint="test",
        )
        admin.register_view(view)

        login_as_admin()

        rv = client.post(
            "/admin/test/new",
            data={"id": "1", "name": "test", "value": "hello"},
            follow_redirects=True,
        )
        assert rv.status_code == 200

        rv = client.post(
            "/admin/test/new",
            data={"id": "1", "name": "test", "value": "world"},
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert "Already exists." in rv.text

        with force_locale("zh"):
            rv = client.post(
                "/admin/test/new",
                data={"id": "1", "name": "test", "value": "world"},
                follow_redirects=True,
            )
            assert rv.status_code == 200
            assert "已经存在" in rv.text
