import pytest
from datetime import datetime, time, date
from wtforms import fields, validators
from flask_exts.admin.sqla import filter
from flask_exts.template.form.base_form import BaseForm
from flask_exts.template.fields import Select2Field
from flask_exts.admin.sqla.view import SqlaModelView
from flask_exts.datastore.sqla import db
from flask_exts.datastore.sqla.orm import InstrumentedAttribute
from flask_exts.datastore.sqla.utils import get_field_with_path
from flask_exts.datastore.sqla.utils import is_hybrid_property
from tests.datastore.sqla.models.model1 import EnumChoices
from tests.datastore.sqla.models.model1 import Model1, Model2, Model3

class CustomFilterModelView(SqlaModelView):
    def __init__(
        self,
        model,
        name=None,
        endpoint=None,
        url=None,
        **kwargs,
    ):
        for k, v in kwargs.items():
            setattr(self, k, v)

        super().__init__(model, name=name, endpoint=endpoint, url=url)

    form_choices = {"choice_field": [("choice-1", "One"), ("choice-2", "Two")]}


def fill_db():
    model1_obj1 = Model1(test1="test1_val_1", test2="test2_val_1", bool_field=True)
    model1_obj2 = Model1(test1="test1_val_2", test2="test2_val_2", bool_field=False)
    model1_obj3 = Model1(test1="test1_val_3", test2="test2_val_3")
    model1_obj4 = Model1(test1="test1_val_4", test2="test2_val_4", choice_field="choice-1")

    model2_obj1 = Model2(string_field="test2_val_1", model1=model1_obj1, float_field=None)
    model2_obj2 = Model2(string_field="test2_val_2", model1=model1_obj2, float_field=None)
    model2_obj3 = Model2(string_field="test2_val_3", int_field=5000, float_field=25.9)
    model2_obj4 = Model2(string_field="test2_val_4", int_field=9000, float_field=75.5)
    model2_obj5 = Model2(string_field="test2_val_5", int_field=6169453081680413441)
    

def test_column_filters(app, client, admin):
    with app.app_context():
        db.reset_all()

        view1 = CustomFilterModelView(Model1, name="view1", column_filters=["test1"])
        admin.add_view(view1)

        assert len(view1._filters) == 7

        # Generate views
        view2 = CustomFilterModelView(Model2, name="view2", column_filters=["model1.test1","model1.test2"])

        view5 = CustomFilterModelView(
            Model1, name="view5", column_filters=["test1"], endpoint="_strings"
        )
        admin.add_view(view5)

        view6 = CustomFilterModelView(Model2, name="view6", column_filters=["int_field"])
        admin.add_view(view6)

        view7 = CustomFilterModelView(
            Model1, name="view7", column_filters=["bool_field"], endpoint="_bools"
        )
        admin.add_view(view7)

        view8 = CustomFilterModelView(
            Model2, name="view8", column_filters=["float_field"], endpoint="_float"
        )
        admin.add_view(view8)

        view9 = CustomFilterModelView(
            Model2,
            name="view9",
            endpoint="_model2",
            column_filters=["model1.bool_field"],
            column_list=[
                "string_field",
                "model1.id",
                "model1.bool_field",
            ],
        )
        admin.add_view(view9)

        view10 = CustomFilterModelView(
            Model1,
            name="view10",
            column_filters=["test1"],
            endpoint="_model3",
            named_filter_urls=True,
        )
        admin.add_view(view10)

        view11 = CustomFilterModelView(
            Model1,
            name="view11",
            column_filters=["date_field", "datetime_field", "time_field"],
            endpoint="_datetime",
        )
        admin.add_view(view11)

        view12 = CustomFilterModelView(
            Model1, name="view12", column_filters=["enum_field"], endpoint="_enumfield"
        )
        admin.add_view(view12)

        view13 = CustomFilterModelView(
            Model2,
            name="view13",
            column_filters=[filter.FilterEqual(Model1.test1, "Test1")],
            endpoint="_relation_test",
        )
        admin.add_view(view13)

        view14 = CustomFilterModelView(
            Model1,
            name="view14",
            column_filters=["enum_type_field"],
            endpoint="_enumtypefield",
        )
        admin.add_view(view14)

        # Test views
        assert [
            (f["index"], f["operation"]) for f in view1._filter_groups["Test1"]
        ] == [
            (0, "contains"),
            (1, "not contains"),
            (2, "equals"),
            (3, "not equal"),
            (4, "empty"),
            (5, "in list"),
            (6, "not in list"),
        ]

        # Test filter that references property0
        print(view2._filter_groups)


        assert [
            (f["index"], f["operation"]) for f in view2._filter_groups["Model1 / Test1"]
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
            (f["index"], f["operation"]) for f in view2._filter_groups["Model1 / Test2"]
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
            (f["index"], f["operation"]) for f in view2._filter_groups["Model1 / Test3"]
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
            (f["index"], f["operation"]) for f in view2._filter_groups["Model1 / Test4"]
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
            for f in view2._filter_groups["Model1 / Bool Field"]
        ] == [
            (28, "equals"),
            (29, "not equal"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view2._filter_groups["Model1 / Date Field"]
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
            for f in view2._filter_groups["Model1 / Time Field"]
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
            for f in view2._filter_groups["Model1 / Datetime Field"]
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
            for f in view2._filter_groups["Model1 / Email Field"]
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
            for f in view2._filter_groups["Model1 / Enum Field"]
        ] == [
            (58, "equals"),
            (59, "not equal"),
            (60, "empty"),
            (61, "in list"),
            (62, "not in list"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view2._filter_groups["Model1 / Enum Type Field"]
        ] == [
            (63, "equals"),
            (64, "not equal"),
            (65, "empty"),
            (66, "in list"),
            (67, "not in list"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view2._filter_groups["Model1 / Choice Field"]
        ] == [
            (68, "contains"),
            (69, "not contains"),
            (70, "equals"),
            (71, "not equal"),
            (72, "empty"),
            (73, "in list"),
            (74, "not in list"),
        ]

        # Test filter with a dot
        view3 = CustomFilterModelView(
            Model2, name="view3", column_filters=["model1.bool_field"]
        )

        assert [
            (f["index"], f["operation"])
            for f in view3._filter_groups["model1 / Model1 / Bool Field"]
        ] == [
            (0, "equals"),
            (1, "not equal"),
        ]

        # Test column_labels on filters
        view4 = CustomFilterModelView(
            Model2,
            name="view4",
            column_filters=["model1.bool_field", "string_field"],
            column_labels={
                "model1.bool_field": "Test Filter #1",
                "string_field": "Test Filter #2",
            },
        )

        assert list(view4._filter_groups.keys()) == ["Test Filter #1", "Test Filter #2"]

        fill_db()

        # Test equals
        rv = client.get("/admin/model1/?flt0_0=test1_val_1")
        assert rv.status_code == 200
        # the filter value is always in "data"
        # need to check a different column than test1 for the expected row
        assert "test2_val_1" in rv.text
        assert "test1_val_2" not in rv.text

        # Test NOT IN filter
        rv = client.get("/admin/model1/?flt0_6=test1_val_1")
        assert rv.status_code == 200
        assert "test1_val_2" in rv.text
        assert "test2_val_1" not in rv.text

        # Test string filter
        assert [
            (f["index"], f["operation"]) for f in view5._filter_groups["Test1"]
        ] == [
            (0, "contains"),
            (1, "not contains"),
            (2, "equals"),
            (3, "not equal"),
            (4, "empty"),
            (5, "in list"),
            (6, "not in list"),
        ]

        # string - equals
        rv = client.get("/admin/_strings/?flt0_0=test1_val_1")
        assert rv.status_code == 200
        assert "test2_val_1" in rv.text
        assert "test1_val_2" not in rv.text

        # string - not equal
        rv = client.get("/admin/_strings/?flt0_1=test1_val_1")
        assert rv.status_code == 200
        assert "test2_val_1" not in rv.text
        assert "test1_val_2" in rv.text

        # string - contains
        rv = client.get("/admin/_strings/?flt0_2=test1_val_1")
        assert rv.status_code == 200
        assert "test2_val_1" in rv.text
        assert "test1_val_2" not in rv.text

        # string - not contains
        rv = client.get("/admin/_strings/?flt0_3=test1_val_1")
        assert rv.status_code == 200
        assert "test2_val_1" not in rv.text
        assert "test1_val_2" in rv.text

        # string - empty
        rv = client.get("/admin/_strings/?flt0_4=1")
        assert rv.status_code == 200
        assert "empty_obj" in rv.text
        assert "test1_val_1" not in rv.text
        assert "test1_val_2" not in rv.text

        # string - not empty
        rv = client.get("/admin/_strings/?flt0_4=0")
        assert rv.status_code == 200
        assert "empty_obj" not in rv.text
        assert "test1_val_1" in rv.text
        assert "test1_val_2" in rv.text

        # string - in list
        rv = client.get("/admin/_strings/?flt0_5=test1_val_1%2Ctest1_val_2")
        assert rv.status_code == 200
        assert "test2_val_1" in rv.text
        assert "test2_val_2" in rv.text
        assert "test1_val_3" not in rv.text
        assert "test1_val_4" not in rv.text

        # string - not in list
        rv = client.get("/admin/_strings/?flt0_6=test1_val_1%2Ctest1_val_2")
        assert rv.status_code == 200
        assert "test2_val_1" not in rv.text
        assert "test2_val_2" not in rv.text
        assert "test1_val_3" in rv.text
        assert "test1_val_4" in rv.text

        # Test integer filter
        assert [
            (f["index"], f["operation"]) for f in view6._filter_groups["Int Field"]
        ] == [
            (0, "equals"),
            (1, "not equal"),
            (2, "greater than"),
            (3, "smaller than"),
            (4, "empty"),
            (5, "in list"),
            (6, "not in list"),
        ]

        # integer - equals
        rv = client.get("/admin/model2/?flt0_0=5000")
        assert rv.status_code == 200
        assert "test2_val_3" in rv.text
        assert "test2_val_4" not in rv.text

        # integer - equals (huge number)
        rv = client.get("/admin/model2/?flt0_0=6169453081680413441")
        assert rv.status_code == 200
        assert "test2_val_5" in rv.text
        assert "test2_val_4" not in rv.text

        # integer - equals - test validation
        rv = client.get("/admin/model2/?flt0_0=badval")
        assert rv.status_code == 200
        assert "Invalid Filter Value" in rv.text

        # integer - not equal
        rv = client.get("/admin/model2/?flt0_1=5000")
        assert rv.status_code == 200
        assert "test2_val_3" not in rv.text
        assert "test2_val_4" in rv.text

        # integer - greater
        rv = client.get("/admin/model2/?flt0_2=6000")
        assert rv.status_code == 200
        assert "test2_val_3" not in rv.text
        assert "test2_val_4" in rv.text

        # integer - smaller
        rv = client.get("/admin/model2/?flt0_3=6000")
        assert rv.status_code == 200
        assert "test2_val_3" in rv.text
        assert "test2_val_4" not in rv.text

        # integer - empty
        rv = client.get("/admin/model2/?flt0_4=1")
        assert rv.status_code == 200
        assert "test2_val_1" in rv.text
        assert "test2_val_2" in rv.text
        assert "test2_val_3" not in rv.text
        assert "test2_val_4" not in rv.text

        # integer - not empty
        rv = client.get("/admin/model2/?flt0_4=0")
        assert rv.status_code == 200
        assert "test2_val_1" not in rv.text
        assert "test2_val_2" not in rv.text
        assert "test2_val_3" in rv.text
        assert "test2_val_4" in rv.text

        # integer - in list
        rv = client.get("/admin/model2/?flt0_5=5000%2C9000")
        assert rv.status_code == 200
        assert "test2_val_1" not in rv.text
        assert "test2_val_2" not in rv.text
        assert "test2_val_3" in rv.text
        assert "test2_val_4" in rv.text

        # integer - in list (huge number)
        rv = client.get("/admin/model2/?flt0_5=6169453081680413441")
        assert rv.status_code == 200
        assert "test2_val_1" not in rv.text
        assert "test2_val_5" in rv.text

        # integer - in list - test validation
        rv = client.get("/admin/model2/?flt0_5=5000%2Cbadval")
        assert rv.status_code == 200
        assert "Invalid Filter Value" in rv.text

        # integer - not in list
        rv = client.get("/admin/model2/?flt0_6=5000%2C9000")
        assert rv.status_code == 200
        assert "test2_val_1" in rv.text
        assert "test2_val_2" in rv.text
        assert "test2_val_3" not in rv.text
        assert "test2_val_4" not in rv.text

        # Test boolean filter
        assert [
            (f["index"], f["operation"]) for f in view7._filter_groups["Bool Field"]
        ] == [
            (0, "equals"),
            (1, "not equal"),
        ]

        # boolean - equals - Yes
        rv = client.get("/admin/_bools/?flt0_0=1")
        assert rv.status_code == 200
        assert "test2_val_1" in rv.text
        assert "test2_val_2" not in rv.text
        assert "test2_val_3" not in rv.text

        # boolean - equals - No
        rv = client.get("/admin/_bools/?flt0_0=0")
        assert rv.status_code == 200
        assert "test2_val_1" not in rv.text
        assert "test2_val_2" in rv.text
        assert "test2_val_3" in rv.text

        # boolean - not equals - Yes
        rv = client.get("/admin/_bools/?flt0_1=1")
        assert rv.status_code == 200
        assert "test2_val_1" not in rv.text
        assert "test2_val_2" in rv.text
        assert "test2_val_3" in rv.text

        # boolean - not equals - No
        rv = client.get("/admin/_bools/?flt0_1=0")
        assert rv.status_code == 200
        assert "test2_val_1" in rv.text
        assert "test2_val_2" not in rv.text
        assert "test2_val_3" not in rv.text

        # Test float filter
        assert [
            (f["index"], f["operation"]) for f in view8._filter_groups["Float Field"]
        ] == [
            (0, "equals"),
            (1, "not equal"),
            (2, "greater than"),
            (3, "smaller than"),
            (4, "empty"),
            (5, "in list"),
            (6, "not in list"),
        ]

        # float - equals
        rv = client.get("/admin/_float/?flt0_0=25.9")
        assert rv.status_code == 200
        assert "test2_val_3" in rv.text
        assert "test2_val_4" not in rv.text

        # float - equals - test validation
        rv = client.get("/admin/_float/?flt0_0=badval")
        assert rv.status_code == 200
        assert "Invalid Filter Value" in rv.text

        # float - not equal
        rv = client.get("/admin/_float/?flt0_1=25.9")
        assert rv.status_code == 200
        assert "test2_val_3" not in rv.text
        assert "test2_val_4" in rv.text

        # float - greater
        rv = client.get("/admin/_float/?flt0_2=60.5")
        assert rv.status_code == 200
        assert "test2_val_3" not in rv.text
        assert "test2_val_4" in rv.text

        # float - smaller
        rv = client.get("/admin/_float/?flt0_3=60.5")
        assert rv.status_code == 200
        assert "test2_val_3" in rv.text
        assert "test2_val_4" not in rv.text

        # float - empty
        rv = client.get("/admin/_float/?flt0_4=1")
        assert rv.status_code == 200
        assert "test2_val_1" in rv.text
        assert "test2_val_2" in rv.text
        assert "test2_val_3" not in rv.text
        assert "test2_val_4" not in rv.text

        # float - not empty
        rv = client.get("/admin/_float/?flt0_4=0")
        assert rv.status_code == 200
        assert "test2_val_1" not in rv.text
        assert "test2_val_2" not in rv.text
        assert "test2_val_3" in rv.text
        assert "test2_val_4" in rv.text

        # float - in list
        rv = client.get("/admin/_float/?flt0_5=25.9%2C75.5")
        assert rv.status_code == 200
        assert "test2_val_1" not in rv.text
        assert "test2_val_2" not in rv.text
        assert "test2_val_3" in rv.text
        assert "test2_val_4" in rv.text

        # float - in list - test validation
        rv = client.get("/admin/_float/?flt0_5=25.9%2Cbadval")
        assert rv.status_code == 200
        assert "Invalid Filter Value" in rv.text

        # float - not in list
        rv = client.get("/admin/_float/?flt0_6=25.9%2C75.5")
        assert rv.status_code == 200
        assert "test2_val_1" in rv.text
        assert "test2_val_2" in rv.text
        assert "test2_val_3" not in rv.text
        assert "test2_val_4" not in rv.text

        # Test filters to joined table field
        rv = client.get("/admin/_model2/?flt1_0=1")
        assert rv.status_code == 200
        assert "test2_val_1" in rv.text
        assert "test2_val_2" not in rv.text
        assert "test2_val_3" not in rv.text
        assert "test2_val_4" not in rv.text

        # Test human readable URLs
        rv = client.get("/admin/_model3/?flt1_test1_equals=test1_val_1")
        assert rv.status_code == 200
        assert "test1_val_1" in rv.text
        assert "test1_val_2" not in rv.text

        # Test date, time, and datetime filters
        assert [
            (f["index"], f["operation"]) for f in view11._filter_groups["Date Field"]
        ] == [
            (0, "equals"),
            (1, "not equal"),
            (2, "greater than"),
            (3, "smaller than"),
            (4, "between"),
            (5, "not between"),
            (6, "empty"),
        ]

        assert [
            (f["index"], f["operation"])
            for f in view11._filter_groups["Datetime Field"]
        ] == [
            (7, "equals"),
            (8, "not equal"),
            (9, "greater than"),
            (10, "smaller than"),
            (11, "between"),
            (12, "not between"),
            (13, "empty"),
        ]

        assert [
            (f["index"], f["operation"]) for f in view11._filter_groups["Time Field"]
        ] == [
            (14, "equals"),
            (15, "not equal"),
            (16, "greater than"),
            (17, "smaller than"),
            (18, "between"),
            (19, "not between"),
            (20, "empty"),
        ]

        # date - equals
        rv = client.get("/admin/_datetime/?flt0_0=2014-11-17")
        assert rv.status_code == 200
        assert "date_obj1" in rv.text
        assert "date_obj2" not in rv.text

        # date - not equal
        rv = client.get("/admin/_datetime/?flt0_1=2014-11-17")
        assert rv.status_code == 200
        assert "date_obj1" not in rv.text
        assert "date_obj2" in rv.text

        # date - greater
        rv = client.get("/admin/_datetime/?flt0_2=2014-11-16")
        assert rv.status_code == 200
        assert "date_obj1" in rv.text
        assert "date_obj2" not in rv.text

        # date - smaller
        rv = client.get("/admin/_datetime/?flt0_3=2014-11-16")
        assert rv.status_code == 200
        assert "date_obj1" not in rv.text
        assert "date_obj2" in rv.text

        # date - between
        rv = client.get("/admin/_datetime/?flt0_4=2014-11-13+-+2014-11-20")
        assert rv.status_code == 200
        assert "date_obj1" in rv.text
        assert "date_obj2" not in rv.text

        # date - not between
        rv = client.get("/admin/_datetime/?flt0_5=2014-11-13+-+2014-11-20")
        assert rv.status_code == 200
        assert "date_obj1" not in rv.text
        assert "date_obj2" in rv.text

        # date - empty
        rv = client.get("/admin/_datetime/?flt0_6=1")
        assert rv.status_code == 200
        assert "test1_val_1" in rv.text
        assert "date_obj1" not in rv.text
        assert "date_obj2" not in rv.text

        # date - empty
        rv = client.get("/admin/_datetime/?flt0_6=0")
        assert rv.status_code == 200
        assert "test1_val_1" not in rv.text
        assert "date_obj1" in rv.text
        assert "date_obj2" in rv.text

        # datetime - equals
        rv = client.get("/admin/_datetime/?flt0_7=2014-04-03+01%3A09%3A00")
        assert rv.status_code == 200
        assert "datetime_obj1" in rv.text
        assert "datetime_obj2" not in rv.text

        # datetime - not equal
        rv = client.get("/admin/_datetime/?flt0_8=2014-04-03+01%3A09%3A00")
        assert rv.status_code == 200
        assert "datetime_obj1" not in rv.text
        assert "datetime_obj2" in rv.text

        # datetime - greater
        rv = client.get("/admin/_datetime/?flt0_9=2014-04-03+01%3A08%3A00")
        assert rv.status_code == 200
        assert "datetime_obj1" in rv.text
        assert "datetime_obj2" not in rv.text

        # datetime - smaller
        rv = client.get("/admin/_datetime/?flt0_10=2014-04-03+01%3A08%3A00")
        assert rv.status_code == 200
        assert "datetime_obj1" not in rv.text
        assert "datetime_obj2" in rv.text

        # datetime - between
        rv = client.get(
            "/admin/_datetime/?flt0_11=2014-04-02+00%3A00%3A00+-+2014-11-20+23%3A59%3A59"
        )
        assert rv.status_code == 200
        assert "datetime_obj1" in rv.text
        assert "datetime_obj2" not in rv.text

        # datetime - not between
        rv = client.get(
            "/admin/_datetime/?flt0_12=2014-04-02+00%3A00%3A00+-+2014-11-20+23%3A59%3A59"
        )
        assert rv.status_code == 200
        assert "datetime_obj1" not in rv.text
        assert "datetime_obj2" in rv.text

        # datetime - empty
        rv = client.get("/admin/_datetime/?flt0_13=1")
        assert rv.status_code == 200
        assert "test1_val_1" in rv.text
        assert "datetime_obj1" not in rv.text
        assert "datetime_obj2" not in rv.text

        # datetime - not empty
        rv = client.get("/admin/_datetime/?flt0_13=0")
        assert rv.status_code == 200
        assert "test1_val_1" not in rv.text
        assert "datetime_obj1" in rv.text
        assert "datetime_obj2" in rv.text

        # time - equals
        rv = client.get("/admin/_datetime/?flt0_14=11%3A10%3A09")
        assert rv.status_code == 200
        assert "timeonly_obj1" in rv.text
        assert "timeonly_obj2" not in rv.text

        # time - not equal
        rv = client.get("/admin/_datetime/?flt0_15=11%3A10%3A09")
        assert rv.status_code == 200
        assert "timeonly_obj1" not in rv.text
        assert "timeonly_obj2" in rv.text

        # time - greater
        rv = client.get("/admin/_datetime/?flt0_16=11%3A09%3A09")
        assert rv.status_code == 200
        assert "timeonly_obj1" in rv.text
        assert "timeonly_obj2" not in rv.text

        # time - smaller
        rv = client.get("/admin/_datetime/?flt0_17=11%3A09%3A09")
        assert rv.status_code == 200
        assert "timeonly_obj1" not in rv.text
        assert "timeonly_obj2" in rv.text

        # time - between
        rv = client.get("/admin/_datetime/?flt0_18=10%3A40%3A00+-+11%3A50%3A59")
        assert rv.status_code == 200
        assert "timeonly_obj1" in rv.text
        assert "timeonly_obj2" not in rv.text

        # time - not between
        rv = client.get("/admin/_datetime/?flt0_19=10%3A40%3A00+-+11%3A50%3A59")
        assert rv.status_code == 200
        assert "timeonly_obj1" not in rv.text
        assert "timeonly_obj2" in rv.text

        # time - empty
        rv = client.get("/admin/_datetime/?flt0_20=1")
        assert rv.status_code == 200
        assert "test1_val_1" in rv.text
        assert "timeonly_obj1" not in rv.text
        assert "timeonly_obj2" not in rv.text

        # time - not empty
        rv = client.get("/admin/_datetime/?flt0_20=0")
        assert rv.status_code == 200
        assert "test1_val_1" not in rv.text
        assert "timeonly_obj1" in rv.text
        assert "timeonly_obj2" in rv.text

        # Test enum filter
        # enum - equals
        rv = client.get("/admin/_enumfield/?flt0_0=model1_v1")
        assert rv.status_code == 200
        assert "enum_obj1" in rv.text
        assert "enum_obj2" not in rv.text

        # enum - not equal
        rv = client.get("/admin/_enumfield/?flt0_1=model1_v1")
        assert rv.status_code == 200
        assert "enum_obj1" not in rv.text
        assert "enum_obj2" in rv.text

        # enum - empty
        rv = client.get("/admin/_enumfield/?flt0_2=1")
        assert rv.status_code == 200
        assert "test1_val_1" in rv.text
        assert "enum_obj1" not in rv.text
        assert "enum_obj2" not in rv.text

        # enum - not empty
        rv = client.get("/admin/_enumfield/?flt0_2=0")
        assert rv.status_code == 200
        assert "test1_val_1" not in rv.text
        assert "enum_obj1" in rv.text
        assert "enum_obj2" in rv.text

        # enum - in list
        rv = client.get("/admin/_enumfield/?flt0_3=model1_v1%2Cmodel1_v2")
        assert rv.status_code == 200
        assert "test1_val_1" not in rv.text
        assert "enum_obj1" in rv.text
        assert "enum_obj2" in rv.text

        # enum - not in list
        rv = client.get("/admin/_enumfield/?flt0_4=model1_v1%2Cmodel1_v2")
        assert rv.status_code == 200
        assert "test1_val_1" in rv.text
        assert "enum_obj1" not in rv.text
        assert "enum_obj2" not in rv.text

        # Test enum type filter
        # enum type - equals
        rv = client.get("/admin/_enumtypefield/?flt0_0=first")
        assert rv.status_code == 200
        assert "enum_type_obj1" in rv.text
        assert "enum_type_obj2" not in rv.text

        # enum - not equal
        rv = client.get("/admin/_enumtypefield/?flt0_1=first")
        assert rv.status_code == 200
        assert "enum_type_obj1" not in rv.text
        assert "enum_type_obj2" in rv.text

        # enum - empty
        rv = client.get("/admin/_enumtypefield/?flt0_2=1")
        assert rv.status_code == 200
        assert "test1_val_1" in rv.text
        assert "enum_type_obj1" not in rv.text
        assert "enum_type_obj2" not in rv.text

        # enum - not empty
        rv = client.get("/admin/_enumtypefield/?flt0_2=0")
        assert rv.status_code == 200
        assert "test1_val_1" not in rv.text
        assert "enum_type_obj1" in rv.text
        assert "enum_type_obj2" in rv.text

        # enum - in list
        rv = client.get("/admin/_enumtypefield/?flt0_3=first%2Csecond")
        assert rv.status_code == 200
        assert "test1_val_1" not in rv.text
        assert "enum_type_obj1" in rv.text
        assert "enum_type_obj2" in rv.text

        # enum - not in list
        rv = client.get("/admin/_enumtypefield/?flt0_4=first%2Csecond")
        assert rv.status_code == 200
        assert "test1_val_1" in rv.text
        assert "enum_type_obj1" not in rv.text
        assert "enum_type_obj2" not in rv.text

        # Test single custom filter on relation
        rv = client.get("/admin/_relation_test/?flt1_0=test1_val_1")
        assert "test1_val_1" in rv.text
        assert "test1_val_2" not in rv.text
