from . import (
    ForeignKey,
    Integer,
    Mapped,
    String,
    cast,
    db,
    hybrid_property,
    mapped_column,
    relationship,
)


class HybridPropertyModel(db.Model):
    __tablename__ = "hybrid_property_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    width: Mapped[int]
    height: Mapped[int]

    first_name = Mapped[str]
    last_name = Mapped[str]
    titles: Mapped["HybridPropertyTitleModel"] = relationship(
        back_populates="owner", uselist=True
    )

    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @hybrid_property
    def pixel_count(self):
        return self.width * self.height

    @hybrid_property
    def pixel_count_text(self):
        return str(self.pixel_count())

    @pixel_count_text.expression
    def pixel_count_text(cls):
        return cast(cls.width * cls.height, String)


class HybridPropertyTitleModel(db.Model):
    __tablename__ = "hybrid_property_title_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    name = Mapped[str]
    owner_id = mapped_column(
        Integer, ForeignKey("hybrid_property_model.id", ondelete="CASCADE")
    )
    owner: Mapped[HybridPropertyModel] = relationship(
        back_populates="titles", uselist=False
    )
