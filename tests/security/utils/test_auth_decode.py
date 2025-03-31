import pytest
from jwt import ExpiredSignatureError
from flask_exts.security.utils.jwtcode import jwt_encode
from flask_exts.security.utils.request_user import authorization_decoder
from flask_exts.security.utils.request_user import UnSupportedAuthType


@pytest.mark.parametrize("auth_str, result", [("Basic Ym9iOnBhc3N3b3Jk", "bob")])
def test_auth_docode_basic(app, auth_str, result):
    with app.app_context():
        assert authorization_decoder(auth_str) == result


@pytest.mark.parametrize("auth_str", ["Unsupported Ym9iOnBhc3N3b3Jk"])
def test_auth_docode_exceptions_unsupported(app, auth_str):
    with app.app_context():
        with pytest.raises(UnSupportedAuthType):
            authorization_decoder(auth_str)


@pytest.mark.parametrize(
    "payload,delta",
    [
        ({"identity": "test"}, 10),
        ({"identity": "test"}, -10),
    ],
)
def test_jwt_decode_exceptions_expired(app, payload, delta):
    with app.app_context():
        auth_str = jwt_encode(
            payload,
            app.config.get("JWT_SECRET_KEY"),
            delta=delta,
            algorithm=app.config.get("JWT_HASH"),
        )
        bearer_str = "Bearer " + auth_str
        if delta < 0:
            with pytest.raises(ExpiredSignatureError):
                authorization_decoder(bearer_str)
        else:
            result = authorization_decoder(bearer_str)
            assert result["identity"] == payload["identity"]
