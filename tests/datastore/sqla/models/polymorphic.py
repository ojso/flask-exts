from typing import Optional
from . import db
from . import Mapped
from . import mapped_column


class Employee(db.Model):
    __tablename__ = "employee"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    type: Mapped[str]
    engineer_info: Mapped[Optional[str]]
    manager_info: Mapped[Optional[str]]

    __mapper_args__ = {"polymorphic_identity": "employee", "polymorphic_on": type}


class Engineer(Employee):
    __mapper_args__ = {"polymorphic_identity": "engineer"}


class Manager(Employee):
    __mapper_args__ = {"polymorphic_identity": "manager"}
