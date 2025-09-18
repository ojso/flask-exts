import pytest
from jwt import ExpiredSignatureError
from flask_login import current_user
from flask_exts.datastore.sqla import db
from flask_exts.utils.jwt import jwt_encode
from flask_exts.utils.request_user import authorization_decoder
from flask_exts.utils.request_user import UnSupportedAuthType
from flask_exts.proxies import _userstore


@pytest.mark.parametrize(
    "payload,delta",
    [
        ({"identity": "test"}, None),
        ({"identity": "test"}, 10),
    ],
)
def test_auth_decode(app, payload, delta):
    with app.app_context():
        auth_str = jwt_encode(
            payload,
            delta=delta,
        )
        bearer_str = "Bearer " + auth_str
        result = authorization_decoder(bearer_str)
        assert result["identity"] == payload["identity"]


@pytest.mark.parametrize("auth_str, result", [("Basic Ym9iOnBhc3N3b3Jk", "bob")])
def test_auth_docode_exceptions_unsupportauthtype(app, auth_str, result):
    with app.app_context():
        # try:
        #     authorization_decoder(auth_str)
        # except Exception as e:
        #     print(e)
        #     print(e.payload)
        with pytest.raises(UnSupportedAuthType):
            authorization_decoder(auth_str)


@pytest.mark.parametrize(
    "payload,delta",
    [
        ({"identity": "test"}, -10),
    ],
)
def test_jwt_decode_exceptions_expired(app, payload, delta):
    with app.app_context():
        auth_str = jwt_encode(
            payload,
            delta=delta,
        )
        bearer_str = "Bearer " + auth_str
        with pytest.raises(ExpiredSignatureError):
            authorization_decoder(bearer_str)


@pytest.mark.parametrize(
    "username,password,email",
    [
        ("test", "test", "test@example.com"),
    ],
)
def test_request_user(app, username, password, email):
    with app.app_context():
        db.drop_all()
        db.create_all()
        user, msg = _userstore.create_user(
            username=username,
            password=password,
            email=email,
        )
        assert user is not None
        assert user.id > 0
        token = jwt_encode({"id": user.id})
        headers = {"Authorization": "Bearer " + token}

    with app.test_request_context(headers=headers):
        assert current_user.id == user.id
        assert current_user.username == user.username
