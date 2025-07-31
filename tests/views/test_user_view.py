import pytest
from flask import url_for
from flask import session

from flask_exts.datastore.sqla import db
from flask_exts.views.user_view import UserView
from flask_exts.template.form.csrf import _get_csrf_token_of_session_and_g


class TestUserView:
    def test_register(self, app, client, admin):
        # app.config.update(CSRF_ENABLED=False)
        with app.app_context():
            admin.add_view(UserView())
            db.create_all()

        with app.test_request_context():
            user_login_url = url_for("user.login")
            user_register_url = url_for("user.register")
            user_logout_url = url_for("user.logout")
            sess_csrf_token, csrf_token = _get_csrf_token_of_session_and_g()

        with client.session_transaction() as sess:
            sess["csrf_token"] = sess_csrf_token

        # register
        test_username = "test1234"
        test_password = "test1234"
        test_email = "test1234@test.com"
        rv = client.post(
            user_register_url,
            data={
                "username": test_username,
                "password": test_password,
                "password_repeat": test_password,
                "email": test_email,
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        with client.session_transaction() as sess:
            assert "_user_id" in sess

        # logout
        client.get(user_logout_url)
        with client.session_transaction() as sess:
            assert "_user_id" not in sess

        # login with invalid name
        test_invalid_name = "invalid_user_name"
        rv = client.post(
            user_login_url,
            data={
                "username": test_invalid_name,
                "password": test_password,
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert "invalid username" in rv.text
        
        # login with valid name
        rv = client.post(
            user_login_url,
            data={
                "username": test_username,
                "password": test_password,
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )
        assert rv.status_code == 200
        with client.session_transaction() as sess:
            assert "_user_id" in sess
        assert test_username in rv.text
