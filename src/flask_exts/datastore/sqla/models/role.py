from datetime import datetime
from typing import Optional

from .. import db
from ..orm import Mapped
from ..orm import mapped_column
from ..orm import ForeignKey
from ..orm import relationship


class Role(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[Optional[str]]
    # recursive relationship
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("role.id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )

    parent = relationship("Role", back_populates="children", remote_side=id)
    children = relationship("Role", back_populates="parent")
