from datetime import datetime
import enum
from typing import Optional, List
# from typing import Literal

from . import db
from . import Enum
from . import JSON
from . import Mapped
from . import mapped_column
from . import relationship
from . import composite
from . import synonym
from . import Table
from . import Column
from . import ForeignKey
from . import hybrid_property
from . import hybrid_method
from . import association_proxy
from . import AssociationProxy

class Point:
    x: int
    y: int

# Status = Literal["pending", "received", "completed"]
class Status(enum.Enum):
    PENDING = "pending"
    RECEIVED = "received"
    COMPLETED = "completed"


class Demo(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    data: Mapped[dict] = mapped_column(JSON)
    x: Mapped[int]
    y: Mapped[int]
    start: Mapped[int]
    end: Mapped[int]
    status: Mapped[Status]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )
    point: Mapped[Point] = composite("x", "y")

    syn_status = synonym("status")

    @hybrid_property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @hybrid_method
    def contains(self, point: int) -> bool:
        return (self.start <= point) & (point <= self.end)

    kw: Mapped[List["Keyword"]] = relationship(secondary=lambda: demo_keyword_table)
    # proxy the 'keyword' attribute from the 'kw' relationship
    keywords: AssociationProxy[List[str]] = association_proxy("kw", "keyword")

    addresses: Mapped[List["Address"]] = relationship(back_populates="demo")

    def __init__(self, name: str):
        self.name = name

class Address(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    street: Mapped[str]
    demo_id = mapped_column(ForeignKey("demo.id"))    
    demo: Mapped["Demo"] = relationship(back_populates="addresses")


class Keyword(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str]

    def __init__(self, keyword: str):
        self.keyword = keyword

    def __repr__(self) -> str:
        return f"Keyword({self.keyword!r})"


demo_keyword_table = Table(
    "demo_keyword",
    db.Model.metadata,
    Column("demo_id", ForeignKey("demo.id"), primary_key=True),
    Column("keyword_id", ForeignKey("keyword.id"), primary_key=True),
)
