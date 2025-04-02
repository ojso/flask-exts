import pytest
import os
from flask import request, jsonify
from casbin.persist.adapters import FileAdapter
from flask_exts.security.authorize.casbin_sqlalchemy_adapter import CasbinRule
from flask_exts.datastore.sqla import db
from flask_exts.security.decorators import auth_required

@pytest.fixture
def enforcer_file_adapter(app):
    adapter = FileAdapter(
        os.path.split(os.path.realpath(__file__))[0] + "/casbin_files/rbac_policy.csv"
    )
    c = app.extensions["security"].casbin
    c.adapter = adapter
    yield c


def init_adapter(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        s = db.session
        s.add(CasbinRule(ptype="p", v0="alice", v1="/item", v2="GET"))
        s.add(CasbinRule(ptype="p", v0="bob", v1="/item", v2="GET"))
        s.add(CasbinRule(ptype="p", v0="data2_admin", v1="/item", v2="POST"))
        s.add(CasbinRule(ptype="p", v0="data2_admin", v1="/item", v2="DELETE"))
        s.add(CasbinRule(ptype="p", v0="data2_admin", v1="/item", v2="GET"))
        s.add(CasbinRule(ptype="g", v0="alice", v1="data2_admin"))
        s.add(CasbinRule(ptype="g", v0="users", v1="data2_admin"))
        s.add(CasbinRule(ptype="g", v0="group with space", v1="data2_admin"))
        db.session.commit()

@pytest.fixture
def enforcer(app):
    c = app.extensions["security"].casbin
    yield c

@pytest.fixture
def watcher():
    class SomeWatcher:
        def should_reload(self):
            return True

        def update_callback(self):
            pass

    yield SomeWatcher


@pytest.mark.parametrize(
    "header, user, method, status",
    [
        (
            "Authorization",
            "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZGVudGl0eSI6ImJvYiJ9."
            "LM-CqxAM2MtT2uT3AO69rZ3WJ81nnyMQicizh4oqBwk",
            "GET",
            200,
        ),
        # (
        #     "Authorization",
        #     "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9."
        #     "eyJleHAiOjE2MTUxMDg0OTIuNTY5MjksImlkZW50aXR5IjoiQm9iIn0."
        #     "CAeMpG-gKbucHU7-KMiqM7H_gTkHSRvXSjNtlvh5DlE",
        #     "GET",
        #     401,
        # ),
        ("Authorization", "Unsupported Ym9iOnBhc3N3b3Jk", "GET", 401),
    ],
)
def test_enforcer(app, client, enforcer, header, user, method, status):
    init_adapter(app)

    @app.route("/a")
    @auth_required
    def index():
        return jsonify({"message": "passed"}), 200

    @app.route("/item", methods=["GET", "POST", "DELETE"])
    @auth_required
    def item():
        if request.method == "GET":
            return jsonify({"message": "passed"}), 200
        elif request.method == "POST":
            return jsonify({"message": "passed"}), 200
        elif request.method == "DELETE":
            return jsonify({"message": "passed"}), 200

    headers = {header: user}
    # client.post('/add', data=dict(title='2nd Item', text='The text'))
    rv = client.get("/a")
    # print(rv.get_data(as_text=True))
    # print(rv.status_code)
    assert rv.status_code == 401
    caller = getattr(client, method.lower())
    rv = caller("/item", headers=headers)
    print(rv.text)
    assert rv.status_code == status

