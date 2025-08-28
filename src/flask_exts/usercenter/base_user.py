from flask_login.mixins import UserMixin


class BaseUser(UserMixin):
    @property
    def is_active(self):
        return self.actived
