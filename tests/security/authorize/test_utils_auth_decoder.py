import jwt
import pytest
from flask_exts.security.utils import authorization_decoder
from flask_exts.security.utils import UnSupportedAuthType


@pytest.mark.parametrize("auth_str, result", [("Basic Ym9iOnBhc3N3b3Jk", "bob")])
def test_auth_docode_basic(app, auth_str, result):
    with app.app_context():
        assert authorization_decoder(auth_str) == result


@pytest.mark.parametrize(
    "auth_str, result",
    [
        (
            "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZGVudGl0eSI6IkJvYiJ9"
            ".YZqkPHdrxkkFNg7GNL8g-hRpiD9LPyospO47Mh3iEDk",
            "Bob",
        )
    ],
)
def test_auth_docode_bearer(app, auth_str, result):
    with app.app_context():
        assert authorization_decoder(auth_str) == result


@pytest.mark.parametrize("auth_str", ["Unsupported Ym9iOnBhc3N3b3Jk"])
def test_auth_docode_exceptions_unsupported(app, auth_str):
    with app.app_context():
        with pytest.raises(UnSupportedAuthType):
            authorization_decoder(auth_str)


@pytest.mark.parametrize(
    "auth_str",
    [
        (
            "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MTUxMDg0OTIuNTY5MjksImlkZW50aXR5IjoiQm9iIn0."
            "CAeMpG-gKbucHU7-KMiqM7H_gTkHSRvXSjNtlvh5DlE"
        )
    ],
)
def test_auth_docode_exceptions_expired(app, auth_str):
    with app.app_context():
        with pytest.raises(jwt.ExpiredSignatureError):
            authorization_decoder(auth_str)
