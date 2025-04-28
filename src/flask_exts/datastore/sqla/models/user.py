from datetime import datetime
from typing import Optional
from typing import List
import uuid
from flask_login import UserMixin
from sqlalchemy import event
from .. import db
from ..orm import Mapped
from ..orm import mapped_column
from ..orm import relationship
from ..orm import ForeignKey
from ..orm import Table
from ..orm import Column


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(unique=True)
    username: Mapped[Optional[str]] = mapped_column(unique=True)
    password: Mapped[Optional[str]]
    email: Mapped[Optional[str]] = mapped_column(unique=True)
    phone_number: Mapped[Optional[str]] = mapped_column(unique=True)
    active: Mapped[bool]
    status: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )

    def __init__(self, username=None, password=None, email=None, phone_number=None):
        self.username = username
        self.password = password
        self.email = email
        self.phone_number = phone_number
        self.active = False
        self.status = 0

    roles: Mapped[List["Role"]] = relationship(secondary="user_role_table")

    profile: Mapped["UserProfile"] = relationship(
        "UserProfile", back_populates="user", uselist=False
    )

    def get_roles(self):
        return [r.name for r in self.roles]


@event.listens_for(User, "before_insert")
def receive_before_insert(mapper, connection, target):
    "listen for the 'before_insert' event"
    if target.uuid is None:
        target.uuid = str(uuid.uuid4())

class UserProfile(db.Model):
    __tablename__ = "user_profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True)
    name: Mapped[Optional[str]]
    identity: Mapped[Optional[str]] = mapped_column(unique=True)
    nickname: Mapped[Optional[str]]
    avatar: Mapped[Optional[str]]
    locale: Mapped[Optional[str]]
    timezone: Mapped[Optional[str]]
    confirmed_at: Mapped[Optional[datetime]]
    # 2FA
    tf_method: Mapped[Optional[str]]
    tf_totp_secret: Mapped[Optional[str]]
    recovery_codes: Mapped[Optional[str]]
    # timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )

    user: Mapped["User"] = relationship("User", back_populates="profile")

class Role(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )

user_role_table = Table(
    "user_role",
    db.Model.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("role_id", ForeignKey("role.id"), primary_key=True),
)