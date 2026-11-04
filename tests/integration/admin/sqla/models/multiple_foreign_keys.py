from . import ForeignKey, Mapped, db, mapped_column, relationship


class MultipleForeignKeyTargetModel(db.Model):
    __tablename__ = "multiple_foreign_key_target_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    kind: Mapped[str]

    first_sources = relationship(
        "MultipleForeignKeySourceModel",
        foreign_keys="MultipleForeignKeySourceModel.first_target_id",
        back_populates="first_target",
    )
    second_sources = relationship(
        "MultipleForeignKeySourceModel",
        foreign_keys="MultipleForeignKeySourceModel.second_target_id",
        back_populates="second_target",
    )
    children = relationship("MultipleForeignKeyChildModel", back_populates="parent")


class MultipleForeignKeySourceModel(db.Model):
    __tablename__ = "multiple_foreign_key_source_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    first_target_id: Mapped[int] = mapped_column(
        ForeignKey("multiple_foreign_key_target_model.id")
    )
    second_target_id: Mapped[int] = mapped_column(
        ForeignKey("multiple_foreign_key_target_model.id")
    )

    first_target = relationship(
        "MultipleForeignKeyTargetModel",
        foreign_keys=[first_target_id],
        back_populates="first_sources",
    )
    second_target = relationship(
        "MultipleForeignKeyTargetModel",
        foreign_keys=[second_target_id],
        back_populates="second_sources",
    )


class MultipleForeignKeyChildModel(db.Model):
    __tablename__ = "multiple_foreign_key_child_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    quantity: Mapped[int]
    parent_id: Mapped[int] = mapped_column(
        ForeignKey("multiple_foreign_key_target_model.id")
    )

    parent = relationship("MultipleForeignKeyTargetModel", back_populates="children")
