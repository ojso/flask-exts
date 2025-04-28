from . import db
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Tree(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    # recursive relationship
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tree.id"))
    parent = relationship("Tree", back_populates="children", remote_side=id)
    children = relationship("Tree", back_populates="parent")

    def __str__(self):
        return "{}".format(self.name)
