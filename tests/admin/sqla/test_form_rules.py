import pytest
from flask_exts.exforms import rules
from ...models import reset_models
from ...models.model1 import Model1, Model2
from .test_basic import CustomModelView


def test_form_rules(app, client, admin):
    with app.app_context():
        reset_models()
        view = CustomModelView(
            Model1, form_rules=("test2", "test1", rules.Field("test4"))
        )
        admin.add_view(view)
        rv = client.get("/admin/model1/new/")
        assert rv.status_code == 200

        # data = rv.data.decode('utf-8')
        data = rv.text
        pos1 = data.find("Test1")
        pos2 = data.find("Test2")
        pos3 = data.find("Test3")
        pos4 = data.find("Test4")
        assert pos1 > pos2
        assert pos4 > pos1
        assert pos3 == -1


def test_rule_header(app, client, admin):
    with app.app_context():
        reset_models()

        view = CustomModelView(Model1, form_create_rules=(rules.Header("hello"),))
        admin.add_view(view)

        rv = client.get("/admin/model1/new/")
        assert rv.status_code == 200

        data = rv.data.decode("utf-8")
        assert "<h3>hello</h3>" in data


def test_rule_field_set(app, client, admin):
    with app.app_context():
        reset_models()
        view = CustomModelView(
            Model1,
            form_create_rules=(rules.FieldSet(["test2", "test1", "test4"], "header"),),
        )
        admin.add_view(view)

        rv = client.get("/admin/model1/new/")
        assert rv.status_code == 200

        data = rv.data.decode("utf-8")
        assert "<h3>header</h3>" in data
        pos1 = data.find("Test1")
        pos2 = data.find("Test2")
        pos3 = data.find("Test3")
        pos4 = data.find("Test4")
        assert pos1 > pos2
        assert pos4 > pos1
        assert pos3 == -1


def test_rule_inlinefieldlist(app, client, admin):
    with app.app_context():
        reset_models()
        view = CustomModelView(
            Model1,
            inline_models=(Model2,),
            form_create_rules=("test1", "model2"),
        )
        admin.add_view(view)

        rv = client.get("/admin/model1/new/")
        assert rv.status_code == 200


def test_inline_model_rules(app, client, admin):
    with app.app_context():
        reset_models()
        view = CustomModelView(
            Model1,
            inline_models=[(Model2, dict(form_rules=("string_field", "bool_field")))],
        )
        admin.add_view(view)

        rv = client.get("/admin/model1/new/")
        assert rv.status_code == 200

        data = rv.data.decode("utf-8")
        assert "int_field" not in data
