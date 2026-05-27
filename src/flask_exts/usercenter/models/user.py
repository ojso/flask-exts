from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from sqlalchemy.ext.mutable import MutableList
from . import db
from ..base_user import BaseUser
from .user_profile import UserProfile
from .role import Role
from .user_role import user_role_table


class User(db.Model, BaseUser):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(unique=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[Optional[str]] = mapped_column(unique=True)
    password: Mapped[Optional[str]]
    actived: Mapped[bool] = mapped_column(default=False)
    status: Mapped[int] = mapped_column(default=0)
    expired_at: Mapped[Optional[datetime]]
    email: Mapped[Optional[str]] = mapped_column(unique=True)
    email_verified: Mapped[bool] = mapped_column(default=False)
    email_verified_at: Mapped[Optional[datetime]]
    phone_number: Mapped[Optional[str]] = mapped_column(unique=True)
    phone_verified: Mapped[bool] = mapped_column(default=False)
    phone_verified_at: Mapped[Optional[datetime]]
    tfa_enabled: Mapped[bool] = mapped_column(default=False)
    tfa_method: Mapped[Optional[str]]
    totp_secret: Mapped[Optional[str]]
    recovery_codes: Mapped[Optional[list[str]]] = mapped_column(
        type_=MutableList.as_mutable(JSON)
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )

    roles: Mapped[list["Role"]] = relationship(secondary="user_role")
    profile: Mapped["UserProfile"] = relationship(back_populates="user", uselist=False)

    def get_roles(self):
        return [r.name for r in self.roles]

    @property
    def is_active(self):
        return self.actived

    @property
    def is_authenticated(self):
        return True
