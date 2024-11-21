from abc import ABC, abstractmethod
from flask_login import UserMixin
from .forms import LoginForm
from .forms import RegisterForm


class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


class UserCenter(ABC):
    login_view = "user.login"

    @abstractmethod
    def user_loader(self, id): ...


class DefaultUserCenter(UserCenter):
    login_form_class = LoginForm
    register_form_class = RegisterForm

    def __init__(self):
        self.users = [User(1, "test", "test")]

    def user_loader(self, user_id):
        u = filter(lambda u: u.id == int(user_id), self.users)
        return next(u, None)

    def get_user_by_username(self, username):
        u = filter(lambda u: u.username == username, self.users)
        return next(u, None)

    def validate_login(self, username, password):
        user = self.get_user_by_username(username)
        return user.password == password
