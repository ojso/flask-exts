import pytest
from flask import url_for
from flask import abort
from flask import request
from flask import session
from flask import g
from flask_exts.admin.admin import Admin

admin = Admin()


class TestUserView:
    def test_register(self, app, client):
        admin.init_app(app)

        with app.test_request_context():
            user_login_url = url_for("user.login")
            user_register_url = url_for("user.register")
            user_logout_url = url_for("user.logout")

        with client:
            rv = client.post(
                user_login_url,
                data={
                    "username": "test1234",
                    "password": "test1234",
                },
            )
            assert rv.status_code == 200
            assert "invalid username" in rv.get_data(as_text=True)
            assert "_user_id" not in session

            rv = client.get(user_register_url)
            assert rv.status_code == 200

            rv = client.post(
                user_register_url,
                data={
                    "username": "test1234",
                    "password": "test1234",
                    "password_repeat": "test1234",
                    "email": "test1234@test.com",
                    # "csrf_token": g.get("csrf_token")
                },
                # follow_redirects=True,
            )

            assert rv.status_code == 302
            assert "_user_id" in session
            client.get(user_logout_url)
            assert "_user_id" not in session

            # test that successful registration redirects to the login page
            rv = client.post(
                user_login_url,
                data={
                    "username": "test1234",
                    "password": "test1234",
                },
                follow_redirects=True,
            )
            assert rv.status_code == 200
            assert "_user_id" in session
            assert "test1234" in rv.get_data(as_text=True)
