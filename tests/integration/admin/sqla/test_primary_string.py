from sqlalchemy.orm import Mapped, mapped_column

from flask_exts.datastore.sqla import db


class PrimaryStringModel(db.Model):
    __tablename__ = "primary_string_model"

    id: Mapped[str] = mapped_column(primary_key=True, autoincrement=False)
    test: Mapped[str]


def test_string_pk(app, client, admin, sqla_view_factory, login_as_admin):
    with app.app_context():
        db.reset_all()
        view = sqla_view_factory(
            PrimaryStringModel, endpoint="test", create_form_columns=["id", "test"]
        )
        admin.register_view(view)

        print(view.create_form_columns)

        login_as_admin()

        rv = client.get("/admin/test/")
        assert rv.status_code == 200

        rv = client.post(
            "/admin/test/new/",
            data={"id": "test1", "test": "test2"},
            follow_redirects=True,
        )
        assert rv.status_code == 200

        rv = client.get("/admin/test/")
        assert rv.status_code == 200
        assert "test1" in rv.text
        assert "test2" in rv.text
