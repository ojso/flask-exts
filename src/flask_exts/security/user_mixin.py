from flask_login.mixins import UserMixin as FlaskLoginUserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class UserMixin(FlaskLoginUserMixin):
    def hash_password(self, password):
        return generate_password_hash(password, method="scrypt")

    def check_password(self, password):
        return check_password_hash(self.password, password)
