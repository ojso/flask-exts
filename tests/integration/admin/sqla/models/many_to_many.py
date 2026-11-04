from . import (
    Column,
    ForeignKey,
    Integer,
    Mapped,
    Table,
    db,
    mapped_column,
    relationship,
)

association_table = Table(
    "many_to_many_association_table",
    db.Model.metadata,
    Column(
        "left_id",
        Integer,
        ForeignKey("many_to_many_left_model.id"),
        primary_key=True,
    ),
    Column(
        "right_id",
        Integer,
        ForeignKey("many_to_many_right_model.id"),
        primary_key=True,
    ),
)


class ManyToManyLeftModel(db.Model):
    __tablename__ = "many_to_many_left_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    rights: Mapped[list["ManyToManyRightModel"]] = relationship(
        secondary=association_table, back_populates="lefts"
    )

    def __str__(self):
        return str(self.name)


class ManyToManyRightModel(db.Model):
    __tablename__ = "many_to_many_right_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    lefts: Mapped[list["ManyToManyLeftModel"]] = relationship(
        secondary=association_table, back_populates="rights"
    )
