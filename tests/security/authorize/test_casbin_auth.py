import pytest
import os
from flask import request, jsonify
from casbin.persist.adapters import FileAdapter
from flask_exts.security.authorize.casbin_sqlalchemy_adapter import CasbinRule
from flask_exts.datastore.sqla import db
from flask_exts.decorators import auth_required
from flask_exts.utils.jwt import jwt_encode
from flask_exts.proxies import current_usercenter
from flask_exts.security.authorize.casbin_authorizer import casbin_prefix_userid


@pytest.fixture
def enforcer_file_adapter(app):
    adapter = FileAdapter(
        os.path.split(os.path.realpath(__file__))[0] + "/casbin_files/rbac_policy.csv"
    )
    c = app.extensions["security"].casbin
    c.adapter = adapter
    yield c


def init_data(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        s = db.session

        u_alice,msg_alice = current_usercenter.register_user(username="alice")
        u_bob,msg_bob = current_usercenter.register_user(username="bob")
        u_cathy,msg_bob = current_usercenter.register_user(username="cathy")

        s.add(CasbinRule(ptype="p", v0=casbin_prefix_userid(u_alice.id), v1="/item", v2="GET"))
        s.add(CasbinRule(ptype="p", v0=casbin_prefix_userid(u_bob.id), v1="/item", v2="GET"))
        s.add(CasbinRule(ptype="p", v0="data2_admin", v1="/item", v2="POST"))
        s.add(CasbinRule(ptype="p", v0="data2_admin", v1="/item", v2="DELETE"))
        s.add(CasbinRule(ptype="p", v0="data2_admin", v1="/item", v2="GET"))
        s.add(CasbinRule(ptype="g", v0="alice", v1="data2_admin"))
        s.add(CasbinRule(ptype="g", v0="users", v1="data2_admin"))
        s.add(CasbinRule(ptype="g", v0="group with space", v1="data2_admin"))
        s.commit()


@pytest.fixture
def watcher():
    class SomeWatcher:
        def should_reload(self):
            return True

        def update_callback(self):
            pass

    yield SomeWatcher


@pytest.mark.parametrize(
    "header, username, method, status",
    [
        (
            "Authorization",
            "alice",
            "GET",
            200,
        ),
        (
            "Authorization",
            "bob",
            "GET",
            200,
        ),
        (
            "Authorization",
            "cathy",
            "GET",
            403,
        ),
    ],
)
def test_enforcer(app, client, header, username, method, status):
    init_data(app)

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

    with app.app_context():
        u = current_usercenter.get_user_by_username(username)
        token = jwt_encode({"id": u.id})
    headers = {header: "Bearer " + token}
    rv = client.get("/a")
    # print(rv.get_data(as_text=True))
    # print(rv.status_code)
    assert rv.status_code == 401
    caller = getattr(client, method.lower())
    rv = caller("/item", headers=headers)
    # print(rv.text)
    assert rv.status_code == status
