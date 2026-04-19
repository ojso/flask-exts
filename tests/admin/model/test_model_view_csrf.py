from flask import session
from wtforms.fields import StringField
from flask_exts.admin.model.view import ModelView
from flask_exts.template.forms.form.csrf import get_csrf_token


class MockModel:
    def __init__(self, id, col=None):
        self.id = id
        self.col = col


class MockModelView(ModelView):
    def __init__(self, model):
        super().__init__(model)
        self.models = []

    def get_last_id(self):
        return len(self.models) + 1

    def get_pk_value(self, model):
        return model.id

    def get_one(self, id):
        return next((model for model in self.models if model.id == int(id)), None)

    def get_list(self, page, sort_field, sort_desc, search, filters, page_size=None):
        return len(self.models), self.models

    def scaffold_form(self):
        class Form(self.form_base_class):
            col = StringField()

        return Form

    def scaffold_list_columns(self):
        return ["id", "col"]

    def scaffold_sortable_columns(self):
        return ["col"]

    def create_model(self, form):
        id = self.get_last_id()
        model = MockModel(id)
        form.populate_obj(model)
        self.models.append(model)
        return model

    def update_model(self, form, model):
        form.populate_obj(model)
        return True

    def delete_model(self, model):
        self.models.remove(model)
        return True

def test_mockview_without_csrf(app, client, admin):
    app.config.update(CSRF_ENABLED=False)

    view = MockModelView(MockModel)
    admin.add_view(view)

    # Model view requests
    rv = client.get("/admin/mockmodel/")
    assert rv.status_code == 200

    # Test model creation view
    rv = client.get("/admin/mockmodel/new/")
    assert rv.status_code == 200
    assert 'name="csrf_token"' not in rv.text

    rv = client.post("/admin/mockmodel/new/", data=dict(col="test"))
    assert rv.status_code == 302
    assert len(view.models) == 1
    model = view.models[0]
    assert model.id == 1
    assert model.col == "test"

    # model edit view
    rv = client.get("/admin/mockmodel/edit/?id=1")
    assert rv.status_code == 200
    assert 'name="csrf_token"' not in rv.text

    rv = client.post(
        "/admin/mockmodel/edit/?id=1",
        data=dict(col="updated_test"),
    )
    assert rv.status_code == 302
    model = view.models[0]
    assert model.id == 1
    assert model.col == "updated_test"

    # delete model
    rv = client.post("/admin/mockmodel/delete/", data=dict(id=1), follow_redirects=True)
    assert "Record was successfully deleted." in rv.text
    assert len(view.models) == 0

def test_mockview_with_csrf(app, client, admin):
    app.config.update(CSRF_ENABLED=True)

    with app.test_request_context():
        csrf_token = get_csrf_token()
        session_csrf_token = session.get("csrf_token")
    with client.session_transaction() as sess:
        sess["csrf_token"] = session_csrf_token

    view = MockModelView(MockModel)
    admin.add_view(view)

    # Model view requests
    rv = client.get("/admin/mockmodel/")
    assert rv.status_code == 200

    # Test model creation view
    rv = client.get("/admin/mockmodel/new/")
    assert rv.status_code == 200
    assert 'name="csrf_token"' in rv.text

    # Create without CSRF token
    rv = client.post("/admin/mockmodel/new/", data=dict(col="test"))
    assert rv.status_code == 200
    assert len(view.models) == 0

    # Create with CSRF token
    rv = client.post(
        "/admin/mockmodel/new/",
        data=dict(col="test", csrf_token=csrf_token),
    )
    assert rv.status_code == 302
    assert len(view.models) == 1
    model = view.models[0]
    assert model.id == 1
    assert model.col == "test"

    # model edit view
    rv = client.get("/admin/mockmodel/edit/?id=1")
    assert rv.status_code == 200
    assert 'name="csrf_token"' in rv.text

    # Edit without CSRF token
    rv = client.post(
        "/admin/mockmodel/edit/?id=1",
        data=dict(col="updated_test"),
    )

    assert rv.status_code == 200
    model = view.models[0]
    assert model.id == 1
    assert model.col == "test"

    # Edit with CSRF token
    rv = client.post(
        "/admin/mockmodel/edit/?id=1",
        data=dict(col="updated_test", csrf_token=csrf_token),
    )
    assert rv.status_code == 302
    assert len(view.models) == 1
    model = view.models[0]
    assert model.id == 1
    assert model.col == "updated_test"

    # Attempt to delete model
    rv = client.post("/admin/mockmodel/delete/", data=dict(id=1), follow_redirects=True)
    assert "Failed to delete record." in rv.text

    rv = client.post("/admin/mockmodel/delete/", data=dict(id=1, csrf_token=csrf_token), follow_redirects=True)
    assert "Record was successfully deleted." in rv.text

