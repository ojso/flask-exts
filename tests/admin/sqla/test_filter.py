import pytest
from flask_exts.datastore.sqla import db
from flask_exts.admin.sqla import filter
from flask_exts.admin.sqla.view import SqlaModelView
from tests.models.demo import Model1, Model2
from .custom_sqla_model_view import CustomSqlaModelView


class Model2View(SqlaModelView):
    column_filters = ["model1.test1", "model1.test2"]


def test_column_filters(app, client, admin):
    with app.app_context():
        view = CustomSqlaModelView(Model1, name="view1", column_filters=["test1"])
        admin.add_view(view)
        assert len(view._filters) == 7
        assert len(view._filter_groups) == 1
        # print(view._filters)
        # print(view._filter_groups)
        assert [(f["index"], f["operation"]) for f in view._filter_groups["test1"]] == [
            (0, "contains"),
            (1, "not contains"),
            (2, "equals"),
            (3, "not equal"),
            (4, "empty"),
            (5, "in list"),
            (6, "not in list"),
        ]


def test_relation_column_filters(app, client, admin):
    with app.app_context():
        db.reset_all()

        view = CustomSqlaModelView(
            Model2,
            name="view2",
            column_filters=[
                "model1.test1",
                "model1.test2",
                "model1.test3",
                "model1.test4",
                "model1.bool_field",
                "model1.date_field",
                "model1.time_field",
                "model1.datetime_field",
                "model1.email_field",
                "model1.enum_field",
            ],
        )
        # print(view._filters)
        # print(view._filter_groups)

        assert [
            (f["index"], f["operation"]) for f in view._filter_groups["model1.test1"]
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
            (f["index"], f["operation"]) for f in view._filter_groups["model1.test2"]
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
            (f["index"], f["operation"]) for f in view._filter_groups["model1.test3"]
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
            (f["index"], f["operation"]) for f in view._filter_groups["model1.test4"]
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
            for f in view._filter_groups["model1.bool_field"]
        ] == [
            (28, "equals"),
            (29, "not equal"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view._filter_groups["model1.date_field"]
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
            for f in view._filter_groups["model1.time_field"]
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
            for f in view._filter_groups["model1.datetime_field"]
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
            for f in view._filter_groups["model1.email_field"]
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
            for f in view._filter_groups["model1.enum_field"]
        ] == [
            (58, "equals"),
            (59, "not equal"),
            (60, "empty"),
            (61, "in list"),
            (62, "not in list"),
        ]
