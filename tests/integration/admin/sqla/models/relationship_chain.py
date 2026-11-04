from . import ForeignKey, Mapped, db, mapped_column, relationship


class RelationshipChainRootModel(db.Model):
    __tablename__ = "relationship_chain_root_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class RelationshipChainMiddleModel(db.Model):
    __tablename__ = "relationship_chain_middle_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    parent_id: Mapped[int] = mapped_column(
        ForeignKey("relationship_chain_root_model.id")
    )
    parent: Mapped[RelationshipChainRootModel] = relationship()


class RelationshipChainLeafModel(db.Model):
    __tablename__ = "relationship_chain_leaf_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    parent_id: Mapped[int] = mapped_column(
        ForeignKey("relationship_chain_middle_model.id")
    )
    parent: Mapped[RelationshipChainMiddleModel] = relationship()
