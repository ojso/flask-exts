from typing import List
from typing import Set
from .. import db
from .. import Mapped
from .. import mapped_column
from .. import ForeignKey
from .. import relationship
from .. import Table
from .. import Column
from .. import Integer

# One-to-Many Relationship Example


class OneToManyParent(db.Model):
    __tablename__ = "one_to_many_parent_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    children: Mapped[List["ManyToOneChild"]] = relationship()
    children2: Mapped[List["ManyToOneChild2"]] = relationship(back_populates="parent2")
    children3: Mapped[Set["ManyToOneChild3"]] = relationship(back_populates="parent3")


class ManyToOneChild(db.Model):
    __tablename__ = "many_to_one_child_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("one_to_many_parent_table.id"))


class ManyToOneChild2(db.Model):
    __tablename__ = "many_to_one_child_table2"

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("one_to_many_parent_table.id"))
    parent2: Mapped["OneToManyParent"] = relationship(back_populates="children2")


class ManyToOneChild3(db.Model):
    __tablename__ = "many_to_one_child_table3"

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("one_to_many_parent_table.id"))
    parent3: Mapped["OneToManyParent"] = relationship(back_populates="children3")


# One-to-One Relationship Example


class OneToOneParent(db.Model):
    __tablename__ = "one_to_one_parent_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    child: Mapped["OneToOneChild"] = relationship(back_populates="parent")


class OneToOneChild(db.Model):
    __tablename__ = "one_to_one_child_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("one_to_one_parent_table.id"))
    parent: Mapped["OneToOneParent"] = relationship(back_populates="child")


# Many-to-Many Relationship Example
association_table = Table(
    "many_to_many_association_table",
    db.Model.metadata,
    Column("left_id", Integer, ForeignKey("many_to_many_left.id"), primary_key=True),
    Column("right_id", Integer, ForeignKey("many_to_many_right.id"), primary_key=True),
)


class ManyToManyLeft(db.Model):
    __tablename__ = "many_to_many_left"

    id: Mapped[int] = mapped_column(primary_key=True)
    rights: Mapped[List["ManyToManyRight"]] = relationship(
        secondary=association_table, back_populates="lefts"
    )


class ManyToManyRight(db.Model):
    __tablename__ = "many_to_many_right"

    id: Mapped[int] = mapped_column(primary_key=True)
    lefts: Mapped[List["ManyToManyLeft"]] = relationship(
        secondary=association_table, back_populates="rights"
    )
