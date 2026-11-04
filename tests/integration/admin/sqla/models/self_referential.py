from . import ForeignKey, Mapped, db, mapped_column, relationship


class SelfReferentialNodeModel(db.Model):
    __tablename__ = "self_referential_node_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("self_referential_node_model.id")
    )
    parent = relationship(
        "SelfReferentialNodeModel", back_populates="children", remote_side=id
    )
    children = relationship("SelfReferentialNodeModel", back_populates="parent")

    def __str__(self):
        return f"{self.name}"
