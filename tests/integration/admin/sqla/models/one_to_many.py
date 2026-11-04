from . import ForeignKey, Mapped, db, mapped_column, relationship


class OneToManyParentModel(db.Model):
    __tablename__ = "one_to_many_parent_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    children: Mapped[list["OneToManyChildModel"]] = relationship()
    back_populated_children: Mapped[list["OneToManyBackPopulatedChildModel"]] = (
        relationship(back_populates="parent")
    )
    set_children: Mapped[set["OneToManySetChildModel"]] = relationship(
        back_populates="parent"
    )


class OneToManyChildModel(db.Model):
    __tablename__ = "one_to_many_child_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("one_to_many_parent_model.id"))


class OneToManyBackPopulatedChildModel(db.Model):
    __tablename__ = "one_to_many_back_populated_child_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("one_to_many_parent_model.id"))
    parent: Mapped["OneToManyParentModel"] = relationship(
        back_populates="back_populated_children"
    )


class OneToManySetChildModel(db.Model):
    __tablename__ = "one_to_many_set_child_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("one_to_many_parent_model.id"))
    parent: Mapped["OneToManyParentModel"] = relationship(back_populates="set_children")
