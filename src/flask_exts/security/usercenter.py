from abc import ABC, abstractmethod
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select
from flask_login import UserMixin

from ..datastore.sqla import db
from ..datastore.sqla.models.user import User
from .forms import LoginForm
from .forms import RegisterForm


class BaseUserCenter(ABC):
    login_view = "user.login"
    login_form_class = LoginForm
    register_form_class = RegisterForm

    @abstractmethod
    def user_loader(self, id): ...


class SqlaUserCenter(BaseUserCenter):
    user_class = User

    def __init__(self, login_view=None, user_class=None):
        if login_view:
            self.login_view = login_view
        if user_class:
            self.user_class = user_class

    def user_loader(self, user_id):
        u = db.session.get(self.user_class, int(user_id))
        return u

    def get_users(self):
        stmt = select(self.user_class).order_by("id")
        users = db.session.execute(stmt).scalars()
        return users

    def get_user_by_id(self, id:int):
        user = db.session.get(self.user_class, id)
        return user
    
    def get_user_by_uniquifier(self,uniquifier):
        stmt = select(self.user_class).filter_by(uniquifier=uniquifier)
        user = db.session.execute(stmt).scalar()
        return user

    def login_user_by_username_password(self, username, password):
        stmt = select(self.user_class).filter_by(username=username)
        user = db.session.execute(stmt).scalar()
        if user is None:
            return (None, "invalid username")
        elif not check_password_hash(user.password, password):
            return (None, "invalid password")
        else:
            return (user, None)

    def register_user(self, username, password, email):
        stmt_filter_username = select(self.user_class).filter_by(username=username)
        user_exist_username = db.session.execute(stmt_filter_username).scalar()
        if user_exist_username is not None:
            return (None, "invalid username")

        stmt_filter_email = select(self.user_class).filter_by(email=email)
        user_exist_email = db.session.execute(stmt_filter_email).scalar()
        if user_exist_email is not None:
            return (None, "invalid email")

        user = self.user_class(username=username)
        user.password = generate_password_hash(password)
        user.email = email
        db.session.add(user)
        db.session.commit()
        return (user, None)

    def remove_user(self, user_id):
        return NotImplemented


class BaseUser(UserMixin):
    def __init__(self, id=None, username=None, password=None, email=None):
        self.id = id
        self.username = username
        self.password = password
        self.email = email


class MemoryUserCenter(BaseUserCenter):
    user_class = BaseUser

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
        new_id = 1 if not self.users else max([u.id for u in self.users]) + 1
        u = self.user_class(new_id, username, generate_password_hash(password), email)
        self.users.append(u)
        return (u, None)

    def remove_user(self, user_id):
        return NotImplemented
