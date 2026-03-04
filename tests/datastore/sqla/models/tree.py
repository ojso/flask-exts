from typing import Optional
from .. import db
from .. import ForeignKey
from .. import relationship
from .. import Mapped
from .. import mapped_column


class Tree(db.Model):
    __tablename__ = "tree"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    # recursive relationship
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tree.id"))
    parent = relationship("Tree", back_populates="children", remote_side=id)
    children = relationship("Tree", back_populates="parent")

    def __str__(self):
        return "{}".format(self.name)
