from datetime import datetime
from typing import Optional
from ...datastore.sqla import db
from ...datastore.sqla.orm import Mapped
from ...datastore.sqla.orm import mapped_column
from ...datastore.sqla.orm import relationship
from ...datastore.sqla.orm import ForeignKey


class UserProfile(db.Model):
    __tablename__ = "user_profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True)
    name: Mapped[Optional[str]]
    identity: Mapped[Optional[str]] = mapped_column(unique=True)
    display_name: Mapped[Optional[str]]
    avatar: Mapped[Optional[str]]
    locale: Mapped[Optional[str]]
    timezone: Mapped[Optional[str]]
    # timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )

    user: Mapped["User"] = relationship("User", back_populates="profile")  # type: ignore
