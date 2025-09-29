from werkzeug.security import generate_password_hash, check_password_hash
from flask_login.mixins import UserMixin


class BaseUser(UserMixin):
    @property
    def is_active(self):
        return self.actived

    def hash_password(self, password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
