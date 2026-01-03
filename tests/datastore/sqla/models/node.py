from . import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Node(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id = mapped_column(ForeignKey("node.id"))
    data: Mapped[str]
    children = relationship("Node", back_populates="parent")
    parent = relationship("Node", back_populates="children", remote_side=[id])
