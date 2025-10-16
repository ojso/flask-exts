from datetime import datetime
from typing import Optional
from ...datastore.sqla import db
from ...datastore.sqla.orm import Mapped
from ...datastore.sqla.orm import mapped_column


class Role(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )
