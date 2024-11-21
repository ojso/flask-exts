import pytest
from flask import url_for
from flask import abort
from flask import request
from flask import session
from flask_exts.admin.admin import Admin

admin = Admin()


class TestUserView:
    def test_login(self, app, client):
        admin.init_app(app)

        with app.test_request_context():
            user_login_url = url_for("user.login")
            user_register_url = url_for("user.register")
            user_logout_url = url_for("user.logout")
        
        rv = client.get(user_login_url)
        data = rv.get_data(as_text=True)
        assert user_register_url in data
        assert "username" in data
        # assert "email" in data
        assert "password" in data
        assert rv.status_code == 200

        with client:
            rv = client.post(
                user_login_url,
                data={
                    "username": "test",
                    "password": "test",
                },
            )
            # print(response.data)
            assert "_user_id" in session
            client.get(user_logout_url)
            assert "_user_id" not in session

    # def test_register(self, app, client):
    #     url_register = urls["user.register"]
    #     tmp_username = "tmptest"
    #     tmp_password = "tmptest123"
    #     tmp_email = "tmptest@ojso.com"
    #     # 确保即将注册的username不存在
    #     with app.app_context():
    #         stmt = select(User).filter_by(username=tmp_username)
    #         u = db.session.execute(stmt).scalar()
    #         if u is not None:
    #             # print(u)
    #             db.session.delete(u)
    #             db.session.commit()

    #     # test that viewing the page renders without template errors
    #     assert client.get(url_register).status_code == 200

    #     # test that successful registration redirects to the login page
    #     response = client.post(
    #         url_register,
    #         data={
    #             "username": tmp_username,
    #             "email": tmp_email,
    #             "password": tmp_password,
    #             "password_repeat": tmp_password,
    #         },
    #         follow_redirects=True,
    #     )

    #     # print(response.data)
    #     # return

    #     # 重定向并且成功
    #     assert len(response.history) == 1
    #     assert 200 == response.status_code

    #     # 刚注册成功的用户可否正常登录
    #     with client:
    #         auth.login(username=tmp_username, password=tmp_password)
    #         assert "_user_id" in session
    #         auth.logout()

    #     # 删除刚注册成功的用户
    #     with app.app_context():
    #         # test that the user was inserted into the database
    #         stmt = select(User).filter_by(username=tmp_username)
    #         u = db.session.execute(stmt).scalar()
    #         # print(u)
    #         assert u is not None
    #         db.session.delete(u)
    #         db.session.commit()


    # @pytest.mark.parametrize(
    #     ("username", "password", "message"),
    #     (
    #         ("a", "test", b"Invalid username or password"),
    #         ("test", "a", b"Invalid username or password"),
    #     ),
    # )
    # def test_login_invalid(self, client, username, password, message, urls):
    #     url_login = urls["user.login"]
    #     with client:
    #         response = client.post(
    #             url_login,
    #             data={"username": username, "password": password},
    #             follow_redirects=True,
    #         )
    #         # print(response.data)
    #         assert message in response.data

    # def test_profile(self, client, auth, urls):
    #     url_profile = urls["user.profile"]
    #     with client:
    #         response = client.get(url_profile)
    #         assert response.status_code == 302
    #         auth.login()
    #         response = client.get(url_profile)
    #         assert response.status_code == 200
    #         # print(response.data)
    #         assert b"edit" in response.data
