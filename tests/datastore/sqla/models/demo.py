from enum import Enum
from typing import Optional, List
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import composite
from sqlalchemy.schema import ForeignKey
from sqlalchemy.schema import Table
from sqlalchemy.schema import Column
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.associationproxy import AssociationProxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.hybrid import hybrid_method
from . import db


class Point:
    x: int
    y: int


class Demo(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    x: Mapped[int]
    y: Mapped[int]
    start: Mapped[int]
    end: Mapped[int]

    point: Mapped[Point] = composite("x", "y")

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
    demo_id: Mapped[int] = mapped_column(ForeignKey("demo.id"))    
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
