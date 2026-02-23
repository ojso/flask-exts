import enum
from .. import db
from .. import Mapped
from .. import mapped_column


class MyCat(enum.Enum):
    CAT1 = "Category A"
    CAT2 = "Category B"


class Message(db.Model):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]
    sender: Mapped[str]
    recipient: Mapped[str]
    category: Mapped[MyCat] = mapped_column(default=MyCat.CAT1, nullable=False)
