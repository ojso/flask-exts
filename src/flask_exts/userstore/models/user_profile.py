from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from . import db


class UserProfile(db.Model):
    __tablename__ = "user_profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    name: Mapped[Optional[str]]
    identity: Mapped[Optional[str]] = mapped_column(unique=True)
    display_name: Mapped[Optional[str]]
    avatar: Mapped[Optional[str]]
    locale: Mapped[Optional[str]]
    timezone: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )

    user: Mapped["User"] = relationship("User", back_populates="profile")  # type: ignore
