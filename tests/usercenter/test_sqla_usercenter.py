from flask_exts.usercenter.sqla_user_store import SqlaUserStore
from flask_exts.usercenter.models.user import User
from flask_exts.datastore.sqla import db

class TestSqlaUserCenter:
    def test_base(self, app):
        uc = SqlaUserStore()
        assert uc.user_class == User

        with app.app_context():
            db.create_all()
            r, u1 = uc.create_user(username="u1", password="u1", email="u1")
            assert r == "ok"
            assert u1 is not None
            assert u1.id == 1
            assert u1.username == "u1"

            u2 = uc.get_user_by_id(1)
            assert u2.id == 1
            assert u2.username == "u1"

            u3 = uc.get_user_by_identity(1)
            assert u3.id == 1
            assert u3.username == "u1"

            uc.identity_name = "username"
            u4 = uc.get_user_by_identity("u1")
            assert u4.id == 1
            assert u4.username == "u1"

    def test_user_roles(self, app):
        uc = SqlaUserStore()
        with app.app_context():
            db.create_all()
            r, u = uc.create_user(username="u1", password="u1")
            assert r == "ok"
            # roles
            role_admin = uc.create_role("admin")
            role_user = uc.create_role("user")

            uc.user_add_role(u, role_admin)
            uc.user_add_role(u, role_user)

            roles = u.get_roles()
            assert len(roles) == 2
            assert "admin" in roles
            assert "user" in roles


    
