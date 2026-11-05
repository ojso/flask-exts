from flask_exts.datastore.sqla import db

from .models.admin_records import AdminTestModel


def test_configurable_page_size(app, client, admin, sqla_view_factory, login_as_admin):
    with app.app_context():
        db.reset_all()

        db.session.add_all(
            [AdminTestModel(name=str(f"instance-{x + 1:03d}")) for x in range(101)]
        )

        view1 = sqla_view_factory(
            AdminTestModel,
            name="view1",
            endpoint="view1",
            page_size=20,
            can_set_page_size=False,
        )
        admin.register_view(view1)

        view2 = sqla_view_factory(
            AdminTestModel,
            name="view2",
            endpoint="view2",
            page_size=5,
            can_set_page_size=False,
        )
        admin.register_view(view2)

        view3 = sqla_view_factory(
            AdminTestModel,
            name="view3",
            endpoint="view3",
            page_size=20,
            can_set_page_size=True,
        )
        admin.register_view(view3)

        view4 = sqla_view_factory(
            AdminTestModel,
            name="view4",
            endpoint="view4",
            page_size=5,
            page_size_options=(5, 10, 15),
            can_set_page_size=True,
        )
        admin.register_view(view4)

        login_as_admin()

        rv = client.get("/admin/view1/")
        assert "instance-020" in rv.text
        assert "instance-021" not in rv.text

        # `can_set_page_size=False`, so only the default of 20 is available.
        rv = client.get("/admin/view1/?page_size=50")
        assert "instance-020" in rv.text
        assert "instance-021" not in rv.text

        # Check view2, which has `page_size=5` to change the default page size
        rv = client.get("/admin/view2/")
        assert "instance-005" in rv.text
        assert "instance-006" not in rv.text

        # Check view3, which has `can_set_page_size=True`
        rv = client.get("/admin/view3/")
        assert "instance-020" in rv.text
        assert "instance-021" not in rv.text

        rv = client.get("/admin/view3/?page_size=50")
        assert "instance-050" in rv.text
        assert "instance-051" not in rv.text

        rv = client.get("/admin/view3/?page_size=100")
        assert "instance-100" in rv.text
        assert "instance-101" not in rv.text

        # Invalid page sizes are reset to the default
        rv = client.get("/admin/view3/?page_size=1")
        assert "instance-020" in rv.text
        assert "instance-021" not in rv.text

        # Check view4, which has custom `page_size_options`
        rv = client.get("/admin/view4/")
        assert "instance-005" in rv.text
        assert "instance-006" not in rv.text

        # Invalid page sizes are reset to the default
        rv = client.get("/admin/view4/?page_size=1")
        assert "instance-005" in rv.text
        assert "instance-006" not in rv.text

        rv = client.get("/admin/view4/?page_size=10")
        assert "instance-010" in rv.text
        assert "instance-011" not in rv.text

        rv = client.get("/admin/view4/?page_size=15")
        assert "instance-015" in rv.text
        assert "instance-016" not in rv.text


def test_unlimited_page_size(app, admin, sqla_view_factory, login_as_admin):
    with app.app_context():
        db.reset_all()

        db.session.add_all(
            [
                AdminTestModel(name="1"),
                AdminTestModel(name="2"),
                AdminTestModel(name="3"),
                AdminTestModel(name="4"),
                AdminTestModel(name="5"),
                AdminTestModel(name="6"),
                AdminTestModel(name="7"),
                AdminTestModel(name="8"),
                AdminTestModel(name="9"),
                AdminTestModel(name="10"),
                AdminTestModel(name="11"),
                AdminTestModel(name="12"),
                AdminTestModel(name="13"),
                AdminTestModel(name="14"),
                AdminTestModel(name="15"),
                AdminTestModel(name="16"),
                AdminTestModel(name="17"),
                AdminTestModel(name="18"),
                AdminTestModel(name="19"),
                AdminTestModel(name="20"),
                AdminTestModel(name="21"),
            ]
        )

        view = sqla_view_factory(AdminTestModel)

        # test 0 as page_size
        _, data = view.get_list(0, None, None, None, None, page_size=0)
        assert len(data) == 21

        # test False as page_size
        _, data = view.get_list(0, None, None, None, None, page_size=False)
        assert len(data) == 21
