from flask_exts.datastore.sqla import db

from .models.admin_records import AdminTestModel, RelatedAdminTestModel


def test_search_by_configured_columns(
    app, client, admin, sqla_view_factory, login_as_admin
):
    with app.app_context():
        db.reset_all()

        view = sqla_view_factory(
            AdminTestModel, column_searchable_list=["name", "integer_value"]
        )
        admin.register_view(view)

        db.session.add(AdminTestModel(name="model1-test", integer_value=5000))
        db.session.add(AdminTestModel(name="model2-test", integer_value=9000))
        db.session.commit()

        login_as_admin()

        rv = client.get("/admin/admintestmodel/?search=model1")
        assert "model1-test" in rv.text
        assert "model2-test" not in rv.text

        rv = client.get("/admin/admintestmodel/?search=9000")
        assert "model1-test" not in rv.text
        assert "model2-test" in rv.text


def test_search_preserves_extra_query_arguments(
    app, client, admin, sqla_view_factory, login_as_admin
):
    with app.app_context():
        db.reset_all()
        view1 = sqla_view_factory(
            AdminTestModel,
            column_searchable_list=[
                "name",
            ],
        )

        admin.register_view(view1)

        db.session.add(
            RelatedAdminTestModel(
                optional_string="model1-test",
            )
        )
        db.session.commit()

        login_as_admin()

        # check that extra args in the url are propagated as hidden fields in
        # the search form
        rv = client.get("/admin/admintestmodel/?search=model1&foo=bar")
        assert '<input name="foo" type="hidden" value="bar">' in rv.text


def test_filter_preserves_extra_query_arguments(
    app, client, admin, sqla_view_factory, login_as_admin
):
    with app.app_context():
        db.reset_all()

        view1 = sqla_view_factory(
            AdminTestModel,
            column_filters=[
                "integer_value",
            ],
        )
        admin.register_view(view1)

        db.session.add(AdminTestModel(name="model1-test", integer_value=5000))
        db.session.commit()

        login_as_admin()

        # check that extra args in the url are propagated as hidden fields in the  form
        rv = client.get("/admin/admintestmodel/?flt1_0=5000&foo=bar")
        assert '<input name="foo" type="hidden" value="bar">' in rv.text


def test_search_by_related_columns(
    app, client, admin, sqla_view_factory, login_as_admin
):
    with app.app_context():
        db.reset_all()

        view1 = sqla_view_factory(
            RelatedAdminTestModel, column_searchable_list=["admin_record.name"]
        )
        admin.register_view(view1)
        view2 = sqla_view_factory(
            AdminTestModel, column_searchable_list=["related_records.optional_string"]
        )
        admin.register_view(view2)

        m1 = AdminTestModel(name="model1-name-val")
        m2 = AdminTestModel(name="model1-description-val")
        db.session.add(m1)
        db.session.add(m2)
        db.session.add(
            RelatedAdminTestModel(optional_string="model2-name-val", admin_record=m1)
        )
        db.session.add(
            RelatedAdminTestModel(
                optional_string="model2-description-val", admin_record=m2
            )
        )
        db.session.commit()

        login_as_admin()

        # test relation string - 'admin_record.name'
        rv = client.get("/admin/relatedadmintestmodel/?search=model1-name")
        assert "model2-name-val" in rv.text
        assert "model2-description-val" not in rv.text

        # test relation object - RelatedAdminTestModel.optional_string
        rv = client.get("/admin/admintestmodel/?search=model2-name")
        assert "model1-name-val" in rv.text
        assert "model1-description-val" not in rv.text


def test_search_related_columns_without_related_rows(
    app, client, admin, sqla_view_factory, login_as_admin
):
    with app.app_context():
        db.reset_all()

        view = sqla_view_factory(
            AdminTestModel,
            column_searchable_list=["name", "related_records.optional_string"],
        )
        admin.register_view(view)

        db.session.add(AdminTestModel(name="magic string"))
        db.session.commit()

        login_as_admin()

        rv = client.get("/admin/admintestmodel/?search=magic")
        assert "magic string" in rv.text


def test_column_filter_operations(app, client, admin, sqla_view_factory):
    with app.app_context():
        view = sqla_view_factory(AdminTestModel, name="view1", column_filters=["name"])
        admin.register_view(view)
        assert len(view.get_filters()) == 7
        assert len(view.get_filter_groups()) == 1
        # print(view._filters)
        # print(view.get_filter_groups())
        assert [
            (f["index"], f["operation"]) for f in view.get_filter_groups()["name"]
        ] == [
            (0, "contains"),
            (1, "not contains"),
            (2, "equals"),
            (3, "not equal"),
            (4, "empty"),
            (5, "in list"),
            (6, "not in list"),
        ]


def test_related_column_filter_operations(app, client, admin, sqla_view_factory):
    with app.app_context():
        db.reset_all()

        view = sqla_view_factory(
            RelatedAdminTestModel,
            name="view2",
            column_filters=[
                "admin_record.name",
                "admin_record.description",
                "admin_record.short_text",
                "admin_record.long_text",
                "admin_record.boolean_value",
                "admin_record.date_value",
                "admin_record.time_value",
                "admin_record.datetime_value",
                "admin_record.email",
                "admin_record.enum_choice",
            ],
        )
        # print(view._filters)
        # print(view.get_filter_groups())

        assert [
            (f["index"], f["operation"])
            for f in view.get_filter_groups()["admin_record.name"]
        ] == [
            (0, "contains"),
            (1, "not contains"),
            (2, "equals"),
            (3, "not equal"),
            (4, "empty"),
            (5, "in list"),
            (6, "not in list"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view.get_filter_groups()["admin_record.description"]
        ] == [
            (7, "contains"),
            (8, "not contains"),
            (9, "equals"),
            (10, "not equal"),
            (11, "empty"),
            (12, "in list"),
            (13, "not in list"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view.get_filter_groups()["admin_record.short_text"]
        ] == [
            (14, "contains"),
            (15, "not contains"),
            (16, "equals"),
            (17, "not equal"),
            (18, "empty"),
            (19, "in list"),
            (20, "not in list"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view.get_filter_groups()["admin_record.long_text"]
        ] == [
            (21, "contains"),
            (22, "not contains"),
            (23, "equals"),
            (24, "not equal"),
            (25, "empty"),
            (26, "in list"),
            (27, "not in list"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view.get_filter_groups()["admin_record.boolean_value"]
        ] == [
            (28, "equals"),
            (29, "not equal"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view.get_filter_groups()["admin_record.date_value"]
        ] == [
            (30, "equals"),
            (31, "not equal"),
            (32, "greater than"),
            (33, "smaller than"),
            (34, "between"),
            (35, "not between"),
            (36, "empty"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view.get_filter_groups()["admin_record.time_value"]
        ] == [
            (37, "equals"),
            (38, "not equal"),
            (39, "greater than"),
            (40, "smaller than"),
            (41, "between"),
            (42, "not between"),
            (43, "empty"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view.get_filter_groups()["admin_record.datetime_value"]
        ] == [
            (44, "equals"),
            (45, "not equal"),
            (46, "greater than"),
            (47, "smaller than"),
            (48, "between"),
            (49, "not between"),
            (50, "empty"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view.get_filter_groups()["admin_record.email"]
        ] == [
            (51, "contains"),
            (52, "not contains"),
            (53, "equals"),
            (54, "not equal"),
            (55, "empty"),
            (56, "in list"),
            (57, "not in list"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view.get_filter_groups()["admin_record.enum_choice"]
        ] == [
            (58, "equals"),
            (59, "not equal"),
            (60, "empty"),
            (61, "in list"),
            (62, "not in list"),
        ]
