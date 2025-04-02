import pytest
from jwt import ExpiredSignatureError
from flask_exts.utils.jwt import jwt_encode
from flask_exts.security.utils.request_user import authorization_decoder
from flask_exts.security.utils.request_user import UnSupportedAuthType


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
            assert authorization_decoder(auth_str)


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
