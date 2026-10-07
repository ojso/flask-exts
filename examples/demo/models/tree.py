from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import db


class Tree(db.Model):
    __tablename__ = "tree"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    # recursive relationship
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("tree.id"))
    parent = relationship("Tree", back_populates="children", remote_side=id)
    children = relationship("Tree", back_populates="parent")

    def __str__(self):
        return f"{self.name}"
