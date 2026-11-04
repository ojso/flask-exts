from . import ForeignKey, Mapped, db, mapped_column, relationship


class OneToOneParentModel(db.Model):
    __tablename__ = "one_to_one_parent_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    child: Mapped["OneToOneChildModel"] = relationship(back_populates="parent")


class OneToOneChildModel(db.Model):
    __tablename__ = "one_to_one_child_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    parent_id: Mapped[int] = mapped_column(ForeignKey("one_to_one_parent_model.id"))
    parent: Mapped["OneToOneParentModel"] = relationship(back_populates="child")
