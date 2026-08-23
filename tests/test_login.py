import pytest
from jwt import ExpiredSignatureError
from flask_login import current_user
from flask_exts.datastore.sqla import db
from flask_exts.extensions.login_ext import jwt_encode, authorization_decoder
from flask_exts.proxies import current_userstore


def test_login(app):
    assert getattr(app, "login_manager", None) is not None


@pytest.mark.parametrize(
    "username,password,email",
    [
        ("test1", "test1", "test1@example.com"),
        ("test2", "test2", "test2@example.com"),
    ],
)
def test_authorization_bearer(app, username, password, email):
    with app.app_context():
        db.drop_all()
        db.create_all()
        status, user = current_userstore.create_user(
            username=username,
            password=password,
            email=email,
        )
        assert status == "ok"
        assert user is not None
        assert user.id > 0
        token = jwt_encode({"id": user.id})
        headers = {"Authorization": "Bearer " + token}

    with app.test_request_context(headers=headers):
        assert current_user.id == user.id
        assert current_user.username == user.username


@pytest.mark.parametrize(
    "payload,delta",
    [
        ({"identity": "test"}, None),
        ({"identity": "test"}, 10),
    ],
)
def test_auth_decode(app, payload, delta):
    with app.app_context():
        authstr = jwt_encode(
            payload,
            delta=delta,
        )
        bearer_str = "Bearer " + authstr
        result = authorization_decoder(bearer_str)
        assert result["identity"] == payload["identity"]


@pytest.mark.parametrize("authstr, result", [("Basic Ym9iOnBhc3N3b3Jk", "bob")])
def test_auth_docode_exceptions_unsupportauthtype(app, authstr, result):
    with app.app_context():
        # try:
        #     authorization_decoder(authstr)
        # except Exception as e:
        #     print(e)
        #     print(e.payload)
        with pytest.raises(Exception):
            authorization_decoder(authstr)


@pytest.mark.parametrize(
    "payload,delta",
    [
        ({"identity": "test"}, -10),
    ],
)
def test_jwt_decode_exceptions_expired(app, payload, delta):
    with app.app_context():
        authstr = jwt_encode(
            payload,
            delta=delta,
        )
        bearer_str = "Bearer " + authstr
        with pytest.raises(ExpiredSignatureError):
            authorization_decoder(bearer_str)
