from flask_exts.datastore.sqla import db
from flask_exts.datastore.sqla.query import Query

from .models.admin_records import AdminTestModel, RelatedAdminTestModel


def test_default_column_sort(app, admin, sqla_view_factory, login_as_admin):
    with app.app_context():
        db.reset_all()

        db.session.add_all(
            [
                AdminTestModel(name="c", description="x"),
                AdminTestModel(name="b", description="x"),
                AdminTestModel(name="a", description="y"),
            ]
        )
        db.session.commit()
        query = Query(AdminTestModel)
        assert db.session.scalar(query.build_count()) == 3

        view1 = sqla_view_factory(
            AdminTestModel, name="view1", column_default_sort="name"
        )
        admin.register_view(view1)

        _, data = view1.get_list(0, None, None, None, None)

        assert len(data) == 3
        assert data[0].name == "a"
        assert data[1].name == "b"
        assert data[2].name == "c"

        # test default sort on renamed columns - with column_list scaffolding
        view2 = sqla_view_factory(
            AdminTestModel,
            name="view2",
            column_default_sort="name",
            column_labels={"name": "blah"},
            endpoint="m1_2",
        )
        admin.register_view(view2)

        _, data = view2.get_list(0, None, None, None, None)

        assert len(data) == 3
        assert data[0].name == "a"
        assert data[1].name == "b"
        assert data[2].name == "c"

        # test default sort on renamed columns - without column_list scaffolding
        view3 = sqla_view_factory(
            AdminTestModel,
            name="view3",
            column_default_sort="name",
            column_labels={"name": "blah"},
            endpoint="m1_3",
            column_list=["name"],
        )
        admin.register_view(view3)

        _, data = view3.get_list(0, None, None, None, None)

        assert len(data) == 3
        assert data[0].name == "a"
        assert data[1].name == "b"
        assert data[2].name == "c"

        # test default sort with multiple columns
        order = [("description", False), ("name", False)]
        view4 = sqla_view_factory(
            AdminTestModel, column_default_sort=order, endpoint="m1_4"
        )
        admin.register_view(view4)

        _, data = view4.get_list(0, None, None, None, None)

        assert len(data) == 3
        assert data[0].name == "b"
        assert data[1].name == "c"
        assert data[2].name == "a"


def test_sort_by_related_columns(app, client, admin, sqla_view_factory, login_as_admin):
    with app.app_context():
        db.reset_all()

        m1 = AdminTestModel(name="c", description="x")
        db.session.add(m1)
        db.session.add(RelatedAdminTestModel(optional_string="c", admin_record=m1))

        m2 = AdminTestModel(name="b", description="x")
        db.session.add(m2)
        db.session.add(RelatedAdminTestModel(optional_string="b", admin_record=m2))

        m3 = AdminTestModel(name="a", description="y")
        db.session.add(m3)
        db.session.add(RelatedAdminTestModel(optional_string="a", admin_record=m3))

        db.session.commit()

        # test sorting on relation string - 'admin_record.name'
        view1 = sqla_view_factory(
            RelatedAdminTestModel,
            name="view1",
            column_list=["optional_string", "admin_record.name"],
            column_sortable_list=["admin_record.name"],
        )
        admin.register_view(view1)
        view2 = sqla_view_factory(
            RelatedAdminTestModel,
            name="view2",
            column_list=["optional_string", "admin_record"],
            column_sortable_list=[
                ("admin_record", ("admin_record.description", "admin_record.name"))
            ],
            endpoint="m1_2",
        )
        admin.register_view(view2)

        login_as_admin()

        rv = client.get("/admin/relatedadmintestmodel/?sort=0")
        assert rv.status_code == 200

        _, data = view1.get_list(
            page=0, sort_field="admin_record.name", sort_desc=False
        )

        assert data[0].admin_record.name == "a"
        assert data[1].admin_record.name == "b"
        assert data[2].admin_record.name == "c"

        # test sorting on multiple columns in related model
        rv = client.get("/admin/m1_2/?sort=0")
        assert rv.status_code == 200

        _, data = view2.get_list(page=0, sort_field="admin_record", sort_desc=False)

        assert data[0].admin_record.name == "b"
        assert data[1].admin_record.name == "c"
        assert data[2].admin_record.name == "a"


def test_default_sort_by_related_column(app, admin, sqla_view_factory, login_as_admin):
    with app.app_context():
        db.reset_all()

        m1 = AdminTestModel(name="b")
        db.session.add(m1)
        db.session.add(RelatedAdminTestModel(optional_string="c", admin_record=m1))

        m2 = AdminTestModel(name="a")
        db.session.add(m2)
        db.session.add(RelatedAdminTestModel(optional_string="c", admin_record=m2))

        db.session.commit()

        view1 = sqla_view_factory(
            RelatedAdminTestModel, name="view1", column_default_sort="admin_record.name"
        )
        admin.register_view(view1)

        _, data = view1.get_list(0, None, None, None, None)

        assert len(data) == 2
        assert data[0].admin_record.name == "a"
        assert data[1].admin_record.name == "b"

        # test column_default_sort on a related table's column object
        view2 = sqla_view_factory(
            RelatedAdminTestModel,
            name="view2",
            endpoint="model2_2",
            column_default_sort=("admin_record.name", False),
        )
        admin.register_view(view2)

        _, data = view2.get_list(0, None, None, None, None)

        assert len(data) == 2
        assert data[0].admin_record.name == "a"
        assert data[1].admin_record.name == "b"
