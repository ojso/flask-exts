import pytest
from flask_login import current_user
from flask_exts.datastore.sqla import db
from flask_exts.security.auth_crypt import jwt_encode
from flask_exts.proxies import _userstore


@pytest.mark.parametrize(
    "username,password,email",
    [
        ("test", "test", "test@example.com"),
    ],
)
def test_authorization_bearer(app, username, password, email):
    with app.app_context():
        db.drop_all()
        db.create_all()
        status, user = _userstore.create_user(
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
