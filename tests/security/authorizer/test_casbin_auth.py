import pytest
import os
from flask import request, jsonify
from casbin.persist.adapters import FileAdapter
from flask_exts.datastore.sqla import db
from flask_exts.utils.decorators import auth_required
from flask_exts.utils.decorators import needs_required
from flask_exts.utils.jwt import jwt_encode
from flask_exts.proxies import _userstore
from flask_exts.security.authorizer.sqlalchemy_adapter import CasbinRule
from flask_exts.security.authorizer.casbin_authorizer import casbin_prefix_user


def file_adapter():
    adapter = FileAdapter(
        os.path.split(os.path.realpath(__file__))[0] + "/casbin_files/rbac_policy.csv"
    )
    return adapter


def init_data(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        s = db.session

        u_alice, msg_alice = _userstore.create_user(username="alice")
        u_bob, msg_bob = _userstore.create_user(username="bob")
        u_cathy, msg_bob = _userstore.create_user(username="cathy")
        u_david, msg_bob = _userstore.create_user(username="david")

        role_admin, _ = _userstore.create_role("admin")
        role_edit, _ = _userstore.create_role("edit")
        role_write, _ = _userstore.create_role("write")
        role_read, _ = _userstore.create_role("read")

        _userstore.user_add_role(u_alice, role_admin)
        _userstore.user_add_role(u_bob, role_edit)
        _userstore.user_add_role(u_cathy, role_write)
        _userstore.user_add_role(u_david, role_read)

        s.add(
            CasbinRule(
                ptype="p", v0=casbin_prefix_user(u_alice.id), v1="/item", v2="GET"
            )
        )
        s.add(
            CasbinRule(ptype="p", v0=casbin_prefix_user(u_bob.id), v1="/item", v2="GET")
        )
        s.add(CasbinRule(ptype="p", v0="data2_admin", v1="/item", v2="POST"))
        s.add(CasbinRule(ptype="p", v0="data2_admin", v1="/item", v2="DELETE"))
        s.add(CasbinRule(ptype="p", v0="data2_admin", v1="/item", v2="GET"))
        s.add(CasbinRule(ptype="g", v0="alice", v1="data2_admin"))
        s.add(CasbinRule(ptype="g", v0="users", v1="data2_admin"))
        s.add(CasbinRule(ptype="g", v0="role:edit", v1="role:write"))
        s.add(CasbinRule(ptype="g", v0="role:write", v1="role:read"))
        s.commit()


@pytest.mark.parametrize(
    "username, method, status,status_read,status_write",
    [
        (
            "alice",
            "GET",
            200,
            200,
            200,
        ),
        (
            "bob",
            "GET",
            200,
            200,
            200,
        ),
        (
            "cathy",
            "GET",
            403,
            200,
            200,
        ),
        ("david", "GET", 403, 200, 403),
    ],
)
def test_enforcer(app, client, username, method, status, status_read, status_write):
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

    @app.route("/needread", methods=["GET", "POST", "DELETE"])
    @needs_required(role_need="read")
    def needread():
        if request.method == "GET":
            return jsonify({"message": "passed"}), 200
        elif request.method == "POST":
            return jsonify({"message": "passed"}), 200
        elif request.method == "DELETE":
            return jsonify({"message": "passed"}), 200

    @app.route("/needwrite", methods=["GET", "POST", "DELETE"])
    @needs_required(role_need="write")
    def needwrite():
        if request.method == "GET":
            return jsonify({"message": "passed"}), 200
        elif request.method == "POST":
            return jsonify({"message": "passed"}), 200
        elif request.method == "DELETE":
            return jsonify({"message": "passed"}), 200

    with app.app_context():
        u = _userstore.get_user_by_username(username)
        token = jwt_encode({"id": u.id})
        # print(token)
    headers = {"Authorization": "Bearer " + token}
    rv = client.get("/a")
    
    # print(rv.text)
    # print(rv.status_code)
    assert rv.status_code == 401
    caller = getattr(client, method.lower())
    rv = caller("/item", headers=headers)
    # print(rv.text)
    assert rv.status_code == status

    rv = caller("/needread", headers=headers)
    # print(rv.text)
    # print(rv.status_code)
    assert rv.status_code == status_read

    rv = caller("/needwrite", headers=headers)
    # print(rv.text)
    # print(rv.status_code)
    assert rv.status_code == status_write
