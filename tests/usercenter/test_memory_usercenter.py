from flask_exts.usercenter.memory_usercenter import MemoryUserCenter
from flask_exts.usercenter.memory_usercenter import User


class TestMemoryUserCenter:
    def test_base(self, app):
        uc = MemoryUserCenter()
        assert uc.user_class == User

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
