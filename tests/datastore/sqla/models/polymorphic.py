from typing import Optional
from .. import db
from .. import Mapped
from .. import mapped_column

# see https://docs.sqlalchemy.org/en/20/orm/inheritance.html#single-inheritance
# see https://docs.sqlalchemy.org/en/20/orm/queryguide/_single_inheritance.html

class Employee(db.Model):
    __tablename__ = "employee"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    type: Mapped[str]

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name!r})"

    __mapper_args__ = {
        "polymorphic_identity": "employee",
        "polymorphic_on": "type",
    }


class Manager(Employee):
    manager_name: Mapped[str] = mapped_column(nullable=True)
    __mapper_args__ = {
        "polymorphic_identity": "manager",
    }


class Engineer(Employee):
    engineer_info: Mapped[str] = mapped_column(nullable=True)
    __mapper_args__ = {
        "polymorphic_identity": "engineer",
    }
