from . import db
from . import ForeignKey
from . import Mapped
from . import mapped_column
from . import relationship


class Node(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id = mapped_column(ForeignKey("node.id"))
    data: Mapped[str]
    children = relationship("Node", back_populates="parent")
    parent = relationship("Node", back_populates="children", remote_side=[id])
