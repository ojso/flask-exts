from datetime import datetime, timedelta

from flask import current_app
from sqlalchemy.sql import select
from werkzeug.security import check_password_hash, generate_password_hash

from ..base import UserStore
from ..exceptions import (
    AccountLockedError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from . import db
from .models import Role, User

_DUMMY_PASSWORD_HASH = generate_password_hash("dummy-password", method="scrypt")

_DEFAULT_MAX_FAILURES = 5
_DEFAULT_LOCKOUT_BASE_SECONDS = 60
_DEFAULT_LOCKOUT_MAX_SECONDS = 3600
_MAX_BACKOFF_EXPONENT = 32


class SqlaUserStore(UserStore):
    user_class = User
    role_class = Role

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
                raise UserAlreadyExistsError("username")
        if email:
            stmt_filter_email = select(self.user_class).filter_by(email=email)
            user_exist_email = db.session.execute(stmt_filter_email).scalar()
            if user_exist_email is not None:
                raise UserAlreadyExistsError("email")
        user = self.user_class()
        if username:
            user.username = username
        if password:
            user.password = user.hash_password(password)
        if email:
            user.email = email
        db.session.add(user)
        db.session.commit()
        return user

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
        """Return a matching user or raise InvalidCredentialsError.

        A locked account raises AccountLockedError before the password is
        checked, so attempts during a lockout cost no password-hash work.
        A successful password check does not clear the failure counter;
        the caller clears it once the whole login flow succeeds, which
        keeps second-factor failures in the same consecutive-attempt count.
        """
        password = password if isinstance(password, str) else ""
        stmt = select(self.user_class).filter_by(username=username)
        user = db.session.execute(stmt).scalar()
        if user is None or not user.password:
            check_password_hash(_DUMMY_PASSWORD_HASH, password)
            raise InvalidCredentialsError
        now = datetime.now()
        if self.is_locked(user, now):
            raise AccountLockedError(user.locked_until, now)
        if not user.check_password(password):
            self.record_login_failure(user, now)
            raise InvalidCredentialsError
        return user

    def is_locked(self, user, now=None):
        """Return True while a failed-login lockout is in effect."""
        if user is None or user.locked_until is None:
            return False
        return user.locked_until > (now or datetime.now())

    def record_login_failure(self, user, now=None):
        """Count one failed authentication step and lock when the limit is hit.

        Password and second-factor failures share the counter because both
        are failed attempts against the same account.
        """
        max_failures, base_seconds, max_seconds = self._lockout_policy()
        now = now or datetime.now()
        count = (user.failed_login_count or 0) + 1
        user.failed_login_count = count
        if count >= max_failures:
            exponent = min(count - max_failures, _MAX_BACKOFF_EXPONENT)
            delay = min(base_seconds * 2**exponent, max_seconds)
            user.locked_until = now + timedelta(seconds=delay)
        db.session.commit()
        return user.locked_until

    def clear_login_failures(self, user):
        """Clear the failed-attempt state after a successful authentication."""
        if user.failed_login_count == 0 and user.locked_until is None:
            return
        user.failed_login_count = 0
        user.locked_until = None
        db.session.commit()

    def _lockout_policy(self):
        max_failures = current_app.config.get(
            "USER_LOGIN_MAX_FAILURES", _DEFAULT_MAX_FAILURES
        )
        base_seconds = current_app.config.get(
            "USER_LOGIN_LOCKOUT_BASE_SECONDS", _DEFAULT_LOCKOUT_BASE_SECONDS
        )
        max_seconds = current_app.config.get(
            "USER_LOGIN_LOCKOUT_MAX_SECONDS", _DEFAULT_LOCKOUT_MAX_SECONDS
        )
        if max_failures < 1:
            raise ValueError("USER_LOGIN_MAX_FAILURES must be at least 1.")
        if base_seconds < 1:
            raise ValueError("USER_LOGIN_LOCKOUT_BASE_SECONDS must be at least 1.")
        if max_seconds < base_seconds:
            raise ValueError(
                "USER_LOGIN_LOCKOUT_MAX_SECONDS must be greater than or equal to "
                "USER_LOGIN_LOCKOUT_BASE_SECONDS."
            )
        return max_failures, base_seconds, max_seconds

    def create_role(self, name):
        r = self.role_class(name=name)
        db.session.add(r)
        db.session.commit()
        return r

    def user_set(self, user, **kwargs):
        for key, value in kwargs.items():
            setattr(user, key, value)
        db.session.commit()

    def user_add_role(self, user, role):
        user.roles.append(role)
        db.session.commit()

    def remove_user(self, user_id):
        return NotImplementedError

    def get_user_identity(self, user):
        return getattr(user, self.identity_name)

    def save_user(self, user):
        if user.id is not None:
            db.session.add(user)
        db.session.commit()
