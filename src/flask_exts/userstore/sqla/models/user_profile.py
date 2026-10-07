from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .. import db


class UserProfile(db.Model):
    __tablename__ = "user_profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    name: Mapped[str | None]
    identity: Mapped[str | None] = mapped_column(unique=True)
    display_name: Mapped[str | None]
    avatar: Mapped[str | None]
    locale: Mapped[str | None]
    timezone: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )

    user: Mapped["User"] = relationship("User", back_populates="profile")  # type: ignore  # noqa: F821, UP037
