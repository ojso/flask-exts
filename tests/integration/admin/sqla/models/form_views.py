from . import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Mapped,
    String,
    db,
    mapped_column,
    relationship,
)


class AdminFormModel(db.Model):
    __tablename__ = "admin_form_model"

    id: Mapped[str] = mapped_column(primary_key=True)
    integer_value = mapped_column(Integer)
    date_time = mapped_column(DateTime)
    text: Mapped[str]
    excluded_text: Mapped[str]
    child: Mapped["RelatedAdminFormModel"] = relationship(
        back_populates="parent_form", uselist=False
    )


class RelatedAdminFormModel(db.Model):
    __tablename__ = "related_admin_form_model"

    id: Mapped[str] = mapped_column(primary_key=True)
    admin_form_id = mapped_column(Integer, ForeignKey(AdminFormModel.id))
    parent_form: Mapped[AdminFormModel] = relationship(
        back_populates="child", uselist=False
    )
    enum_choice = mapped_column(Enum("model1_v1", "model1_v2"), nullable=True)
    choice_value = mapped_column(String, nullable=True)
