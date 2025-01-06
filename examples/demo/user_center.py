from werkzeug.security import generate_password_hash, check_password_hash
from flask_exts.users.user_center import DefaultUserCenter
from .models import db,select
from .models.user import User

class UserCenter(DefaultUserCenter):
    user_class = User

    def __init__(self):
        self.users = []

    def user_loader(self, user_id):
        user = db.session.get(User, int(user_id))
        return user

    def get_users(self):
        stmt = select(User).order_by("id")
        users = db.session.execute(stmt).scalars()
        return users

    def get_user_by_id(self, id):
        user = db.session.get(User, id)
        return user

    def login_user_by_username_password(self, username, password):
        stmt = select(User).filter_by(username=username)
        user = db.session.execute(stmt).scalar()
        if user is None:
            return (None, "invalid username")
        elif not check_password_hash(user.password, password):
            return (None, "invalid password")
        else:
            return (user, None)

    def register_user(self, username, password, email):
        stmt_filter_username = select(User).filter_by(username=username)
        user_filter_username = db.session.execute(stmt_filter_username).scalar()
        if user_filter_username is not None:
            return (None, "invalid username")
        
        stmt_filter_email = select(User).filter_by(email=email)
        user_filter_email = db.session.execute(stmt_filter_email).scalar()
        if user_filter_email is not None:
            return (None, "invalid email")
        
        user = self.user_class(username=username)
        user.password = generate_password_hash(password)
        user.email = email
        db.session.add(user)
        db.session.commit()
        return (user, None)

    def remove_user(self, user_id):
        return NotImplemented
