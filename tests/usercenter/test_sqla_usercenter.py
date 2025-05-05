from flask_exts.usercenter.sqla_usercenter import SqlaUserCenter
from flask_exts.datastore.sqla.models.user import User
from flask_exts.datastore.sqla import db


def reset_models():
    db.drop_all()
    db.create_all()


class TestSqlaUserCenter:
    def test_base(self, app):
        uc = SqlaUserCenter()
        assert uc.user_class == User

        with app.app_context():
            reset_models()
            u1, r = uc.create_user(username="u1", password="u1", email="u1")
            assert r is None
            assert u1.id == 1
            assert u1.username == "u1"

            u2 = uc.get_user_by_id(1)
            assert u2.id == 1
            assert u2.username == "u1"

            u3 = uc.get_user_by_identity(1)
            assert u3.id == 1
            assert u3.username == "u1"

            uc.identity_id = "username"
            u4 = uc.get_user_by_identity("u1")
            assert u4.id == 1
            assert u4.username == "u1"
