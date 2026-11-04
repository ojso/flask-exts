import json

from flask_exts.datastore.sqla import db

from .models.admin_records import AdminTestModel, RelatedAdminTestModel
from .models.many_to_many import ManyToManyLeftModel, ManyToManyRightModel


def test_ajax_foreign_key_field(app, client, admin, sqla_view_factory, login_as_admin):
    with app.app_context():
        db.reset_all()

        view = sqla_view_factory(
            RelatedAdminTestModel,
            url="view",
            ajax_refs={"admin_record": {"fields": ("name", "description")}},
        )
        admin.register_view(view)

        assert "admin_record" in view._ajax_refs

        model1 = AdminTestModel(name="first")
        model2 = AdminTestModel(name="foo", description="bar")
        db.session.add_all([model1, model2])
        db.session.commit()

        # Check loader
        loader = view.get_ajax_loader("admin_record")
        mdl = loader.get_one(model1.id)
        assert mdl.name == model1.name

        items = loader.get_list("fir")
        assert len(items) == 1
        assert items[0].id == model1.id

        items = loader.get_list("bar")
        assert len(items) == 1
        assert items[0].name == "foo"

        # Check form generation
        form = view.create_form()
        assert form.admin_record.__class__.__name__ == "AjaxSelectField"

        login_as_admin()

        with app.test_request_context("/admin/view/"):
            rendered = str(form.admin_record())
            assert "<select " in rendered
            assert 'data-role="tom-select-ajax"' in rendered
            assert 'data-tom-select="ajax"' in rendered
            assert 'value=""' not in form.admin_record()

            form.admin_record.data = model1
            assert (
                f'data-json="[{model1.id}, &quot;first&quot;]"' in form.admin_record()
                or f'data-json="[{model1.id}, &#34;first&#34;]"' in form.admin_record()
            )
            assert 'value="1"' in form.admin_record()

        # Check querying
        req = client.get("/admin/view/ajax/lookup/?name=admin_record&query=foo")
        assert json.loads(req.data.decode("utf-8")) == [[model2.id, "foo"]]

        # Check submitting
        req = client.post(
            "/admin/view/new/",
            data={"optional_string": "model2-test", "admin_record": str(model1.id)},
        )
        mdl = db.session.query(RelatedAdminTestModel).first()

        assert mdl is not None
        assert mdl.admin_record is not None
        assert mdl.admin_record.id == model1.id
        assert mdl.admin_record.name == "first"


def test_ajax_many_to_many_field(app, client, admin, sqla_view_factory, login_as_admin):
    with app.app_context():
        db.reset_all()

        view = sqla_view_factory(
            ManyToManyRightModel,
            url="view",
            ajax_refs={"lefts": {"fields": ["name"]}},
        )
        admin.register_view(view)

        assert "lefts" in view._ajax_refs

        first_model = ManyToManyLeftModel(name="first")
        second_model = ManyToManyLeftModel(name="second")
        db.session.add_all(
            [
                first_model,
                second_model,
                ManyToManyRightModel(name="foo"),
            ]
        )
        db.session.commit()

        # Check form generation
        form = view.create_form()
        assert form.lefts.__class__.__name__ == "AjaxSelectMultipleField"

        login_as_admin()

        with app.test_request_context("/admin/view/"):
            assert 'data-json="[]"' in form.lefts()

            form.lefts.data = [first_model, second_model]
            rendered = form.lefts()
            expected_data = json.dumps(
                [[first_model.id, "first"], [second_model.id, "second"]]
            )
            expected_data_escaped = expected_data.replace('"', "&quot;")
            expected_data_html_escaped = expected_data.replace('"', "&#34;")
            assert (
                f'data-json="{expected_data_escaped}"' in rendered
                or f'data-json="{expected_data_html_escaped}"' in rendered
            )

        # Check submitting
        response = client.post(
            "/admin/view/new/",
            data={
                "name": "created",
                "lefts": f"{first_model.id},{second_model.id}",
            },
        )
        assert response.status_code == 302
        mdl = db.session.query(ManyToManyRightModel).filter_by(name="created").one()

        assert mdl is not None
        assert {related_model.id for related_model in mdl.lefts} == {
            first_model.id,
            second_model.id,
        }
