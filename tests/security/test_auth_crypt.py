import pytest
from jwt import ExpiredSignatureError
from flask_exts.security.auth_crypt import jwt_encode
from flask_exts.security.auth_crypt import authorization_decoder


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
