from datetime import datetime
from typing import Optional
from typing import List
import uuid
from flask_login import UserMixin

# from sqlalchemy import event
from .. import db
from ..orm import Mapped
from ..orm import mapped_column
from ..orm import relationship
from ..orm import ForeignKey
from ..orm import Table
from ..orm import Column
from .role import Role
from .user_profile import UserProfile

user_role_table = Table(
    "user_role",
    db.Model.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("role_id", ForeignKey("role.id"), primary_key=True),
)


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(unique=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[Optional[str]] = mapped_column(unique=True)
    password: Mapped[Optional[str]]
    email: Mapped[Optional[str]] = mapped_column(unique=True)
    phone_number: Mapped[Optional[str]] = mapped_column(unique=True)
    active: Mapped[bool] = mapped_column(default=False)
    status: Mapped[int] = mapped_column(default=0)
    confirmed_at: Mapped[Optional[datetime]]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )

    roles: Mapped[List["Role"]] = relationship(secondary=user_role_table)

    profile: Mapped["UserProfile"] = relationship(
        "UserProfile", back_populates="user", uselist=False
    )

    def get_roles(self):
        return [r.name for r in self.roles]


# @event.listens_for(User, "before_insert")
# def receive_before_insert(mapper, connection, target):
#     "listen for the 'before_insert' event"
#     if target.uuid is None:
#         target.uuid = str(uuid.uuid4())
