import pytest
import os
from flask import request, jsonify
from casbin.enforcer import Enforcer
from casbin.persist.adapters import FileAdapter
from flask_exts.security import CasbinEnforcer


@pytest.fixture
def enforcer(app):
    # from sqlalchemy import create_engine
    # from sqlalchemy.orm import sessionmaker
    # from casbin_sqlalchemy_adapter import Adapter
    # from casbin_sqlalchemy_adapter import Base
    # from casbin_sqlalchemy_adapter import CasbinRule
    # engine = create_engine("sqlite://")
    # adapter = Adapter(engine)

    # session = sessionmaker(bind=engine)
    # Base.metadata.create_all(engine)
    # s = session()
    # s.query(CasbinRule).delete()
    # s.add(CasbinRule(ptype="p", v0="alice", v1="/item", v2="GET"))
    # s.add(CasbinRule(ptype="p", v0="bob", v1="/item", v2="GET"))
    # s.add(CasbinRule(ptype="p", v0="data2_admin", v1="/item", v2="POST"))
    # s.add(CasbinRule(ptype="p", v0="data2_admin", v1="/item", v2="DELETE"))
    # s.add(CasbinRule(ptype="p", v0="data2_admin", v1="/item", v2="GET"))
    # s.add(CasbinRule(ptype="g", v0="alice", v1="data2_admin"))
    # s.add(CasbinRule(ptype="g", v0="users", v1="data2_admin"))
    # s.add(CasbinRule(ptype="g", v0="group with space", v1="data2_admin"))
    # s.commit()
    # s.close()

    adapter = FileAdapter(
        os.path.split(os.path.realpath(__file__))[0] + "/casbin_files/rbac_policy.csv"
    )
    yield CasbinEnforcer(app, adapter=adapter)


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
        ("Authorization", "Basic Ym9iOnBhc3N3b3Jk", "GET", 200),
        (
            "Authorization",
            "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZGVudGl0eSI6ImJvYiJ9."
            "LM-CqxAM2MtT2uT3AO69rZ3WJ81nnyMQicizh4oqBwk",
            "GET",
            200,
        ),
        (
            "Authorization",
            "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9."
            "eyJleHAiOjE2MTUxMDg0OTIuNTY5MjksImlkZW50aXR5IjoiQm9iIn0."
            "CAeMpG-gKbucHU7-KMiqM7H_gTkHSRvXSjNtlvh5DlE",
            "GET",
            401,
        ),
        ("Authorization", "Basic Ym9iOnBhc3N3b3Jk", "GET", 200),
        ("Authorization", "Unsupported Ym9iOnBhc3N3b3Jk", "GET", 401),
    ],
)
def test_enforcer(app, client, enforcer, header, user, method, status):
    @app.route("/")
    @enforcer.enforcer
    def index():
        return jsonify({"message": "passed"}), 200

    @app.route("/item", methods=["GET", "POST", "DELETE"])
    @enforcer.enforcer_header
    def item():
        if request.method == "GET":
            return jsonify({"message": "passed"}), 200
        elif request.method == "POST":
            return jsonify({"message": "passed"}), 200
        elif request.method == "DELETE":
            return jsonify({"message": "passed"}), 200

    headers = {header: user}
    # client.post('/add', data=dict(title='2nd Item', text='The text'))
    rv = client.get("/")
    assert rv.status_code == 401
    caller = getattr(client, method.lower())
    rv = caller("/item", headers=headers)
    assert rv.status_code == status


@pytest.mark.parametrize(
    "header, user, method, status",
    [
        ("Authorization", "Basic Ym9iOnBhc3N3b3Jk", "GET", 200),
        ("Authorization", "Unsupported Ym9iOnBhc3N3b3Jk", "GET", 401),
    ],
)
def test_enforcer_with_watcher(
    app, client, enforcer, header, user, method, status, watcher
):
    enforcer.set_watcher(watcher())

    @app.route("/")
    @enforcer.enforcer
    def index():
        return jsonify({"message": "passed"}), 200

    @app.route("/item", methods=["GET", "POST", "DELETE"])
    @enforcer.enforcer_header
    def item():
        if request.method == "GET":
            return jsonify({"message": "passed"}), 200
        elif request.method == "POST":
            return jsonify({"message": "passed"}), 200
        elif request.method == "DELETE":
            return jsonify({"message": "passed"}), 200

    headers = {header: user}
    # client.post('/add', data=dict(title='2nd Item', text='The text'))
    rv = client.get("/")
    assert rv.status_code == 401
    caller = getattr(client, method.lower())
    rv = caller("/item", headers=headers)
    assert rv.status_code == status


def test_manager(app, client, enforcer):
    @app.route("/manager", methods=["POST"])
    @enforcer.manager
    def manager(manager):
        assert isinstance(manager, Enforcer)
        return jsonify({"message": "passed"}), 200

    client.post("/manager")


def test_enforcer_set_watcher(enforcer, watcher):
    assert enforcer.e.watcher is None
    enforcer.set_watcher(watcher())
    assert isinstance(enforcer.e.watcher, watcher)


@pytest.mark.parametrize(
    "owner, method, status",
    [
        (["alice"], "GET", 200),
        (["alice"], "POST", 200),
        (["alice"], "DELETE", 200),
        (["bob"], "GET", 200),
        (["bob"], "POST", 401),
        (["bob"], "DELETE", 401),
        (["admin"], "GET", 401),
        (["users"], "GET", 200),
        (["alice", "bob"], "POST", 200),
        (["noexist", "testnoexist"], "POST", 401),
    ],
)
def test_enforcer_with_owner_loader(app, client, enforcer, owner, method, status):
    @enforcer.owner_loader
    def owner_loader():
        return owner

    @app.route("/")
    @enforcer.enforcer
    def index():
        return jsonify({"message": "passed"}), 200

    @app.route("/item", methods=["GET", "POST", "DELETE"])
    @enforcer.enforcer
    def item():
        if request.method == "GET":
            return jsonify({"message": "passed"}), 200
        elif request.method == "POST":
            return jsonify({"message": "passed"}), 200
        elif request.method == "DELETE":
            return jsonify({"message": "passed"}), 200

    # client.post('/add', data=dict(title='2nd Item', text='The text'))
    rv = client.get("/")
    assert rv.status_code == 401
    caller = getattr(client, method.lower())
    rv = caller("/item")
    assert rv.status_code == status
