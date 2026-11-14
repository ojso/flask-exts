import pytest
from flask_login import current_user
from jwt import ExpiredSignatureError

from flask_exts.builtin_extensions.login_ext import (
    InvalidAuthorizationError,
    authorization_decoder,
    jwt_decode,
    jwt_encode,
    jwt_encode_for_user,
    password_fingerprint,
)
from flask_exts.datastore.sqla import db
from flask_exts.proxies import current_userstore


def test_base(app):
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
        user = current_userstore.create_user(
            username=username,
            password=password,
            email=email,
        )
        assert user is not None
        assert user.id > 0
        token = jwt_encode_for_user(user)
        headers = {"Authorization": "Bearer " + token}

    with app.test_request_context(headers=headers):
        assert current_user.id == user.id
        assert current_user.username == user.username


def test_bearer_token_without_password_fingerprint_is_rejected(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = current_userstore.create_user(
            username="legacy", password="legacy", email="legacy@example.com"
        )
        token = jwt_encode({"id": user.id})
        headers = {"Authorization": "Bearer " + token}

    with app.test_request_context(headers=headers):
        assert not current_user.is_authenticated


def test_bearer_token_is_rejected_after_password_change(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = current_userstore.create_user(
            username="rotate", password="before", email="rotate@example.com"
        )
        token = jwt_encode_for_user(user)
        user.password = user.hash_password("after")
        db.session.commit()
        headers = {"Authorization": "Bearer " + token}

    with app.test_request_context(headers=headers):
        assert not current_user.is_authenticated


def test_tfa_user_requires_otp_claim(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = current_userstore.create_user(
            username="tfa", password="tfa", email="tfa@example.com"
        )
        user.tfa_enabled = True
        db.session.commit()

        with pytest.raises(ValueError):
            jwt_encode_for_user(user)

        password_only = jwt_encode(
            {
                "id": user.id,
                "pwd": password_fingerprint(user),
                "amr": ["pwd"],
            }
        )
        verified = jwt_encode_for_user(user, amr=["otp"])

    with app.test_request_context(
        headers={"Authorization": "Bearer " + password_only}
    ):
        assert not current_user.is_authenticated
    with app.test_request_context(headers={"Authorization": "Bearer " + verified}):
        assert current_user.id == user.id


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
        assert result["token_use"] == "access"
        assert "exp" in result
        assert "exp" not in payload


@pytest.mark.parametrize("authstr, result", [("Basic Ym9iOnBhc3N3b3Jk", "bob")])
def test_auth_decode_exceptions_unsupported(app, authstr, result):
    with app.app_context(), pytest.raises(InvalidAuthorizationError):
        authorization_decoder(authstr)


@pytest.mark.parametrize("header", ["Bearer", "Bearer a b", "", "Basic token"])
def test_auth_decode_rejects_malformed_headers(app, header):
    with app.app_context(), pytest.raises(InvalidAuthorizationError):
        authorization_decoder(header)


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
        with pytest.raises(InvalidAuthorizationError) as exc_info:
            authorization_decoder(bearer_str)
        assert isinstance(exc_info.value.__cause__, ExpiredSignatureError)


def test_jwt_encode_records_issued_at(app):
    with app.app_context():
        payload = jwt_decode(jwt_encode({"id": 1}))
    assert "iat" in payload
    assert payload["token_use"] == "access"


def test_jwt_decode_honours_configured_leeway(app, monkeypatch):
    with app.app_context():
        token = jwt_encode({"id": 1}, delta=-5)

        monkeypatch.setitem(app.config, "JWT_LEEWAY", 0)
        with pytest.raises(ExpiredSignatureError):
            jwt_decode(token)

        monkeypatch.setitem(app.config, "JWT_LEEWAY", 30)
        assert jwt_decode(token)["id"] == 1


@pytest.mark.parametrize("algorithm", ["none", "hs256", "RS256"])
def test_unsupported_jwt_algorithm_is_rejected(app, algorithm):
    with app.app_context():
        with pytest.raises(RuntimeError, match="Unsupported JWT algorithm"):
            jwt_encode({"id": 1}, algorithm=algorithm)

        token = jwt_encode({"id": 1})
        with pytest.raises(RuntimeError, match="Unsupported JWT algorithm"):
            jwt_decode(token, algorithm=algorithm)


def test_unsupported_configured_jwt_algorithm_is_rejected(app, monkeypatch):
    with app.app_context():
        monkeypatch.setitem(app.config, "JWT_HASH", "none")
        with pytest.raises(RuntimeError, match="Unsupported JWT algorithm"):
            jwt_encode({"id": 1})


def test_jwt_requires_secret_key(app, monkeypatch):
    with app.app_context():
        monkeypatch.delitem(app.config, "JWT_SECRET_KEY")
        with pytest.raises(RuntimeError, match="JWT_SECRET_KEY must be set"):
            jwt_encode({"id": 1})


def test_jwt_rejects_short_secret_key(app, monkeypatch):
    with app.app_context():
        monkeypatch.setitem(app.config, "JWT_SECRET_KEY", "too-short")
        with pytest.raises(RuntimeError, match="at least 32 bytes"):
            jwt_encode({"id": 1})


def test_jwt_rejects_secret_key_shared_with_flask_secret(app, monkeypatch):
    shared = "x" * 32
    with app.app_context():
        monkeypatch.setitem(app.config, "SECRET_KEY", shared)
        monkeypatch.setitem(app.config, "JWT_SECRET_KEY", shared)
        with pytest.raises(RuntimeError, match="must differ from SECRET_KEY"):
            jwt_encode({"id": 1})


def test_jwt_encode_for_user_accepts_amr_string(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = current_userstore.create_user(
            username="amrstring", password="pw", email="amrstring@example.com"
        )
        payload = jwt_decode(jwt_encode_for_user(user, amr="otp"))

    assert payload["amr"] == ["pwd", "otp"]


def test_jwt_encode_for_user_accepts_amr_iterable(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = current_userstore.create_user(
            username="amriter", password="pw", email="amriter@example.com"
        )
        payload = jwt_decode(jwt_encode_for_user(user, amr=("pwd", "otp", "otp")))

    assert payload["amr"] == ["pwd", "otp"]


@pytest.mark.parametrize("amr", [[1], [None], 123, {1, "pwd"}])
def test_jwt_encode_for_user_rejects_invalid_amr(app, amr):
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = current_userstore.create_user(
            username="badamr", password="pw", email="badamr@example.com"
        )
        with pytest.raises(TypeError):
            jwt_encode_for_user(user, amr=amr)


@pytest.mark.parametrize("bad_id", [True, 1.9, "1.0", [1], {"id": 1}])
def test_bearer_token_rejects_non_integer_user_id(app, bad_id):
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = current_userstore.create_user(
            username="badid", password="pw", email="badid@example.com"
        )
        assert user.id == 1
        token = jwt_encode(
            {
                "id": bad_id,
                "pwd": password_fingerprint(user),
                "amr": ["pwd"],
            }
        )
        headers = {"Authorization": "Bearer " + token}

    with app.test_request_context(headers=headers):
        assert not current_user.is_authenticated


def test_bearer_token_accepts_decimal_string_user_id(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = current_userstore.create_user(
            username="strid", password="pw", email="strid@example.com"
        )
        token = jwt_encode(
            {
                "id": str(user.id),
                "pwd": password_fingerprint(user),
                "amr": ["pwd"],
            }
        )
        headers = {"Authorization": "Bearer " + token}

    with app.test_request_context(headers=headers):
        assert current_user.id == user.id


@pytest.mark.parametrize("scheme", ["bearer", "BEARER", "BeArEr"])
def test_bearer_scheme_is_case_insensitive(app, scheme):
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = current_userstore.create_user(
            username="scheme", password="pw", email="scheme@example.com"
        )
        token = jwt_encode_for_user(user)
        headers = {"Authorization": f"{scheme} {token}"}

    with app.test_request_context(headers=headers):
        assert current_user.id == user.id
