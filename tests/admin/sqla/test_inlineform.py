from wtforms import fields
from flask_exts.exforms.form import BaseForm
from flask_exts.admin.sqla import ModelView
from flask_exts.exforms.fields.sqla import InlineModelFormList
from flask_exts.exforms.validators.sqla import ItemsRequired
from ...models import db, reset_models
from ...models.user import MyUser, UserInfo, UserEmail, Tag
from ...models.tree import Tree


def test_inline_form(app, client, admin):
    with app.app_context():
        reset_models()

        class UserModelView(ModelView):
            inline_models = (UserInfo,)

        view = UserModelView(MyUser, endpoint="users")
        admin.add_view(view)

        # Basic tests
        assert view._create_form_class is not None
        assert view._edit_form_class is not None
        assert view.endpoint == "users"

        # Verify form
        assert view._create_form_class.name.field_class == fields.StringField
        assert view._create_form_class.info.field_class == InlineModelFormList

        rv = client.get("/admin/users/")
        assert rv.status_code == 200

        rv = client.get("/admin/users/new/")
        assert rv.status_code == 200

        # Create
        rv = client.post("/admin/users/new/", data=dict(name="äõüxyz"))
        assert rv.status_code == 302
        assert MyUser.query.count() == 1
        assert UserInfo.query.count() == 0

        data = {"name": "fbar", "info-0-key": "foo", "info-0-val": "bar"}
        rv = client.post("/admin/users/new/", data=data)
        assert rv.status_code == 302
        assert MyUser.query.count() == 2
        assert UserInfo.query.count() == 1

        # Edit
        rv = client.get("/admin/users/edit/?id=2")
        assert rv.status_code == 200
        # Edit - update
        data = {
            "name": "barfoo",
            "info-0-id": 1,
            "info-0-key": "xxx",
            "info-0-val": "yyy",
        }
        rv = client.post("/admin/users/edit/?id=2", data=data)
        assert UserInfo.query.count() == 1
        assert UserInfo.query.one().key == "xxx"

        # Edit - add & delete
        data = {
            "name": "barf",
            "del-info-0": "on",
            "info-0-id": "1",
            "info-0-key": "yyy",
            "info-0-val": "xxx",
            "info-1-id": None,
            "info-1-key": "bar",
            "info-1-val": "foo",
        }
        rv = client.post("/admin/users/edit/?id=2", data=data)
        assert rv.status_code == 302
        assert MyUser.query.count() == 2
        assert db.session.get(MyUser, 2).name == "barf"
        assert UserInfo.query.count() == 1
        assert UserInfo.query.one().key == "bar"

        # Delete
        rv = client.post("/admin/users/delete/?id=2")
        assert rv.status_code == 302
        assert MyUser.query.count() == 1
        rv = client.post("/admin/users/delete/?id=1")
        assert rv.status_code == 302
        assert MyUser.query.count() == 0
        assert UserInfo.query.count() == 0


def test_inline_form_required(app, client, admin):
    with app.app_context():
        reset_models()

        class UserModelView(ModelView):
            inline_models = (UserEmail,)
            form_args = {"emails": {"validators": [ItemsRequired()]}}

        view = UserModelView(MyUser, endpoint="users")
        admin.add_view(view)

        # Create
        rv = client.post("/admin/users/new/", data=dict(name="no-email"))
        assert rv.status_code == 200
        assert MyUser.query.count() == 0

        data = {
            "name": "hasEmail",
            "emails-0-email": "foo@bar.com",
        }
        rv = client.post("/admin/users/new/", data=data)
        assert rv.status_code == 302
        assert MyUser.query.count() == 1
        assert UserEmail.query.count() == 1

        # Attempted delete, prevented by ItemsRequired
        data = {
            "name": "hasEmail",
            "del-emails-0": "on",
            "emails-0-email": "foo@bar.com",
        }
        rv = client.post("/admin/users/edit/?id=1", data=data)
        assert rv.status_code == 200
        assert MyUser.query.count() == 1
        assert UserEmail.query.count() == 1


def test_inline_form_ajax_fk(app, admin):
    with app.app_context():
        reset_models()

        class UserModelView(ModelView):
            opts = {"form_ajax_refs": {"tag": {"fields": ["name"]}}}

            inline_models = [(UserInfo, opts)]

        view = UserModelView(MyUser, endpoint="users")
        admin.add_view(view)

        form = view.create_form()
        user_info_form = form.info.unbound_field.args[0]
        loader = user_info_form.tag.args[0]
        assert loader.name == "userinfo-tag"
        assert loader.model == Tag

        assert "userinfo-tag" in view._form_ajax_refs


def test_inline_form_self(app, admin):
    with app.app_context():
        reset_models()

        class TreeView(ModelView):
            inline_models = (Tree,)

        view = TreeView(Tree)

        parent = Tree()
        child = Tree(parent=parent)
        form = view.edit_form(child)
        assert form.parent.data == parent


def test_inline_form_base_class(app, client, admin):
    with app.app_context():
        reset_models()

        # Customize error message
        class StubTranslation:
            def gettext(self, *args):
                return "success!"

            def ngettext(self, *args):
                return "success!"

        class StubBaseForm(BaseForm):
            class Meta:
                def get_translations(self, form):
                    return StubTranslation()

        # Set up Admin
        class UserModelView(ModelView):
            inline_models = ((UserEmail, {"form_base_class": StubBaseForm}),)
            form_args = {"emails": {"validators": [ItemsRequired()]}}

        view = UserModelView(MyUser, endpoint="users")
        admin.add_view(view)

        # Create
        data = {
            "name": "emptyEmail",
            "emails-0-email": "",
        }
        rv = client.post("/admin/users/new/", data=data)
        assert rv.status_code == 200
        assert MyUser.query.count() == 0
        assert b"success!" in rv.data
