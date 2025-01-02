from .usercenter import UserCenter
from werkzeug.security import generate_password_hash, check_password_hash

from .forms import LoginForm
from .forms import RegisterForm


class DefaultUserCenter(UserCenter):
    
    login_form_class = LoginForm
    register_form_class = RegisterForm

    def __init__(self):
        self.users = []

    def user_loader(self, user_id):
        return self.get_user_by_id(int(user_id))

    def get_users(self):
        return self.users

    def get_user_by_id(self, id):
        u = filter(lambda u: u.id == id, self.users)
        return next(u, None)

    def login_user_by_username_password(self, username, password):
        filter_username = filter(lambda u: u.username == username, self.users)
        user = next(filter_username, None)
        if user is None:
            return (None, "invalid username")
        elif not check_password_hash(user.password, password):
            return (None, "invalid password")
        else:
            return (user, None)

    def register_user(self, username, password, email):
        filter_username = filter(lambda u: u.username == username, self.users)
        if next(filter_username, None) is not None:
            return (None, "invalid username")
        filter_email = filter(lambda u: u.email == email, self.users)
        if next(filter_email, None) is not None:
            return (None, "invalid email")
        new_id = 1 if not self.users else max([u.id for u in self.users])+1
        u = self.user_class(
            new_id, username, generate_password_hash(password), email
        )
        self.users.append(u)
        return (u, None)

    def remove_user(self, user_id):
        return NotImplemented
