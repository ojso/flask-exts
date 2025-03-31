from datetime import datetime
from typing import Optional
from typing import List
from flask_login import UserMixin

from .. import db
from ..orm import Mapped
from ..orm import mapped_column
from ..orm import relationship
from .role import Role
from .user_role import user_role_table


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(unique=True)
    password: Mapped[Optional[str]]
    email: Mapped[Optional[str]] = mapped_column(unique=True)
    phonenumber: Mapped[Optional[str]] = mapped_column(unique=True)
    identity: Mapped[Optional[str]] = mapped_column(unique=True)
    uniquifier: Mapped[Optional[str]] = mapped_column(unique=True)
    active: Mapped[Optional[bool]]
    status: Mapped[Optional[int]]
    nickname: Mapped[Optional[str]]
    avatar: Mapped[Optional[str]]
    locale: Mapped[Optional[str]]
    timezone: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )

    roles: Mapped[List["Role"]] = relationship(secondary=user_role_table)
