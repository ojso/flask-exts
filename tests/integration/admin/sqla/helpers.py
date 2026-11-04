from datetime import date, datetime, time

from flask_exts.datastore.sqla import db

from .models.admin_records import AdminEnumChoice, AdminTestModel, RelatedAdminTestModel


def fill_admin_records():
    model1_obj1 = AdminTestModel(
        name="test1_val_1", description="test2_val_1", boolean_value=True
    )
    model1_obj2 = AdminTestModel(
        name="test1_val_2", description="test2_val_2", boolean_value=False
    )
    model1_obj3 = AdminTestModel(name="test1_val_3", description="test2_val_3")
    model1_obj4 = AdminTestModel(
        name="test1_val_4", description="test2_val_4", choice_value="choice-1"
    )

    model2_obj1 = RelatedAdminTestModel(
        optional_string="test2_val_1", admin_record=model1_obj1
    )
    model2_obj2 = RelatedAdminTestModel(
        optional_string="test2_val_2", admin_record=model1_obj2
    )
    model2_obj3 = RelatedAdminTestModel(optional_string="test2_val_3")
    model2_obj4 = RelatedAdminTestModel(optional_string="test2_val_4")
    model2_obj5 = RelatedAdminTestModel(optional_string="test2_val_5")

    date_obj1 = AdminTestModel(name="date_obj1", date_value=date(2014, 11, 17))
    date_obj2 = AdminTestModel(name="date_obj2", date_value=date(2013, 10, 16))
    timeonly_obj1 = AdminTestModel(name="timeonly_obj1", time_value=time(11, 10, 9))
    timeonly_obj2 = AdminTestModel(name="timeonly_obj2", time_value=time(10, 9, 8))
    datetime_obj1 = AdminTestModel(
        name="datetime_obj1", datetime_value=datetime(2014, 4, 3, 1, 9, 0)
    )
    datetime_obj2 = AdminTestModel(
        name="datetime_obj2", datetime_value=datetime(2013, 3, 2, 0, 8, 0)
    )

    enum_obj1 = AdminTestModel(name="enum_type_obj1", enum_choice=AdminEnumChoice.first)
    enum_obj2 = AdminTestModel(
        name="enum_type_obj2", enum_choice=AdminEnumChoice.second
    )

    empty_obj = AdminTestModel(name="empty_obj")

    db.session.add_all(
        [
            model1_obj1,
            model1_obj2,
            model1_obj3,
            model1_obj4,
            model2_obj1,
            model2_obj2,
            model2_obj3,
            model2_obj4,
            model2_obj5,
            date_obj1,
            timeonly_obj1,
            datetime_obj1,
            date_obj2,
            timeonly_obj2,
            datetime_obj2,
            enum_obj1,
            enum_obj2,
            empty_obj,
        ]
    )
    db.session.commit()
