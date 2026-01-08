import enum
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from . import db


class MyCat(enum.Enum):
    CAT1 = "Category A"
    CAT2 = "Category B"


class Message(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]
    sender: Mapped[str]
    recipient: Mapped[str]
    category:Mapped[MyCat] = mapped_column(default=MyCat.CAT1,nullable=False)
    
