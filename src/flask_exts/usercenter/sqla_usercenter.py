from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select
from .base_usercenter import BaseUserCenter
from ..datastore.sqla import db
from ..datastore.sqla.models.user import User
from ..datastore.sqla.models.user import Role


class SqlaUserCenter(BaseUserCenter):
    user_class = User
    role_class = Role

    def __init__(self, user_class=None):
        if user_class:
            self.user_class = user_class

    def user_loader(self, user_id):
        u = db.session.get(self.user_class, int(user_id))
        return u

    def get_users(self, **kwargs):
        stmt = select(self.user_class).order_by("id")
        users = db.session.execute(stmt).scalars()
        return users

    def create_user(self, **kwargs):
        username = kwargs.get("username")
        password = kwargs.get("password")
        email = kwargs.get("email")
        if username:
            stmt_filter_username = select(self.user_class).filter_by(username=username)
            user_exist_username = db.session.execute(stmt_filter_username).scalar()
            if user_exist_username is not None:
                return (None, "invalid username")
        if email:
            stmt_filter_email = select(self.user_class).filter_by(email=email)
            user_exist_email = db.session.execute(stmt_filter_email).scalar()
            if user_exist_email is not None:
                return (None, "invalid email")
        user = self.user_class()
        if username:
            user.username = username
        if password:
            user.password = generate_password_hash(password)
        if email:
            user.email = email
        db.session.add(user)
        db.session.commit()
        return (user, None)

    def get_user_by_id(self, id: int):
        user = db.session.get(self.user_class, id)
        return user

    def get_user_by_identity(self, identity_id, identity_name=None):
        if identity_name is None:
            identity_name = self.identity_name
        stmt = select(self.user_class).filter_by(**{identity_name: identity_id})
        user = db.session.execute(stmt).scalar()
        return user

    def get_user_by_uuid(self, uuid):
        stmt = select(self.user_class).filter_by(uuid=uuid)
        user = db.session.execute(stmt).scalar()
        return user

    def get_user_by_username(self, username):
        stmt = select(self.user_class).filter_by(username=username)
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

    def create_role(self, name):
        r = self.role_class(name=name)
        db.session.add(r)
        db.session.commit()
        return (r, None)

    def user_add_role(self, user, role):
        user.roles.append(role)
        db.session.commit()

    def remove_user(self, user_id):
        return NotImplemented

    def get_user_identity(self, user):
        return getattr(user, self.identity_name)

    def save_user(self, user):
        if user.id is not None:
            db.session.add(user)
        db.session.commit()
