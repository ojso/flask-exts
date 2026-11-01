from sqlalchemy.orm import Mapped, mapped_column

from flask_exts.datastore.sqla import db
from flask_exts.datastore.sqla.query import Query


class MultpkModel(db.Model):
    __tablename__ = "multpk"
    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=False)
    id2: Mapped[int] = mapped_column(primary_key=True,autoincrement=False)
    data: Mapped[str]


def test_multiple_pk(app, client, admin, sqla_view_factory,login_as_admin):

    with app.app_context():
        db.reset_all()
        view = sqla_view_factory(
            MultpkModel,
            endpoint="test",
            create_form_columns=["id", "id2", "data"],
        )
        admin.register_view(view)

        login_as_admin()

        rv = client.get("/admin/test/")
        assert rv.status_code == 200

        rv = client.post(
            "/admin/test/new/", data={"id": 1, "id2": 2, "data": "test_multi"}
        )
        assert rv.status_code == 302

        rv = client.get("/admin/test/")
        assert rv.status_code == 200
        assert "test_multi" in rv.text

        rv = client.get("/admin/test/edit/?id=1,2")
        assert rv.status_code == 200
        assert "test_multi" in rv.text

        rv = client.post(
            "/admin/test/edit/?id=1,2",
            data={"id": 1, "id2": 2, "data": "test_multi_edited"},
        )
        assert rv.status_code == 302

        rv = client.get("/admin/test/details/?id=1,2")
        assert rv.status_code == 200
        assert "test_multi_edited" in rv.text


def test_multiple_pk_delete(app, client, admin, sqla_view_factory, login_as_admin):
    with app.app_context():
        db.reset_all()
        db.session.add_all(
            [
                MultpkModel(id=1, id2=1, data="a"),
                MultpkModel(id=1, id2=2, data="b"),
                MultpkModel(id=2, id2=1, data="c"),
            ]
        )
        db.session.commit()
        query = Query(MultpkModel)
        assert db.session.scalar(query.build_count()) == 3

        view = sqla_view_factory(
            MultpkModel,
            endpoint="test",
            form_columns=["id", "id2", "data"],
        )
        admin.register_view(view)

        login_as_admin()

        rv = client.post(
            "/admin/test/action/", data={"action": "delete", "rowid": ["1, 1", "1, 2"]}
        )
        assert rv.status_code == 302
        assert db.session.scalar(query.build_count()) == 1
