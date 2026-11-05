from flask_exts.datastore.sqla import db

from .helpers import fill_admin_records
from .models.admin_records import AdminTestModel


def test_csv_export(app, client, admin, sqla_view_factory, login_as_admin):
    with app.app_context():
        db.reset_all()

        for x in range(5):
            fill_admin_records()

        view1 = sqla_view_factory(
            AdminTestModel,
            name="view1",
            can_export=True,
            column_list=["name", "description"],
            export_max_rows=2,
            endpoint="row_limit_2",
        )
        admin.register_view(view1)
        view2 = sqla_view_factory(
            AdminTestModel,
            name="view2",
            can_export=True,
            column_list=["name", "description"],
            endpoint="no_row_limit",
        )
        admin.register_view(view2)

        login_as_admin()

        # test export_max_rows
        rv = client.get("/admin/row_limit_2/export/csv/")
        assert rv.status_code == 200
        assert (
            "Name,Description\r\n"
            + "test1_val_1,test2_val_1\r\n"
            + "test1_val_2,test2_val_2\r\n"
            == rv.text
        )

        # test row limit without export_max_rows
        rv = client.get("/admin/no_row_limit/export/csv/")
        assert rv.status_code == 200
        assert len(rv.text.splitlines()) > 21
