import uuid
from datetime import datetime

from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from ....proxies import current_security
from ....security.user_mixin import UserMixin
from .. import db
from .role import Role
from .user_profile import UserProfile
from .user_role import user_role_table


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(unique=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str | None] = mapped_column(unique=True)
    password: Mapped[str | None]
    _is_active: Mapped[bool] = mapped_column("is_active", default=False)
    status: Mapped[int] = mapped_column(default=0)
    expired_at: Mapped[datetime | None]
    email: Mapped[str | None] = mapped_column(unique=True)
    email_verified: Mapped[bool] = mapped_column(default=False)
    email_verified_at: Mapped[datetime | None]
    phone_number: Mapped[str | None] = mapped_column(unique=True)
    phone_verified: Mapped[bool] = mapped_column(default=False)
    phone_verified_at: Mapped[datetime | None]
    tfa_enabled: Mapped[bool] = mapped_column(default=False)
    tfa_method: Mapped[str | None]
    totp_secret: Mapped[str | None]
    recovery_codes: Mapped[list[str] | None] = mapped_column(
        type_=MutableList.as_mutable(JSON)
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )

    roles: Mapped[list["Role"]] = relationship(secondary=user_role_table)
    profile: Mapped["UserProfile"] = relationship(back_populates="user", uselist=False)

    def get_roles(self):
        return [r.name for r in self.roles]

    def get_id(self):
        password_fingerprint  = current_security.hasher.hash(self.password or "")
        return f"{self.id}:{password_fingerprint }"

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value: bool) -> None:
        self._is_active = value

    @property
    def is_authenticated(self):
        return True
