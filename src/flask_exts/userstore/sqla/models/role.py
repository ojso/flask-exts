from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from ...._time import UTCDateTime, utc_now
from .. import db


class Role(db.Model):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=utc_now, onupdate=utc_now
    )
