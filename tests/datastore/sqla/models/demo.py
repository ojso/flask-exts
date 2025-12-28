from enum import Enum
from flask_exts.datastore.sqla import db
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import composite
from sqlalchemy.ext.hybrid import hybrid_property


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

    point: Mapped[Point] = composite("x", "y")

    @hybrid_property
    def full_name_hybrid(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @full_name_hybrid.expression
    def full_name_hybrid(cls):
        return cls.first_name + " " + cls.last_name
