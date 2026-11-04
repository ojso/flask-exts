from datetime import datetime

from . import ForeignKey, Mapped, db, mapped_column, relationship


class InlineDateTimeParentModel(db.Model):
    __tablename__ = "inline_date_time_parent_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    children: Mapped[list["InlineDateTimeChildModel"]] = relationship(
        back_populates="parent"
    )


class InlineDateTimeChildModel(db.Model):
    __tablename__ = "inline_date_time_child_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    occurred_at: Mapped[datetime]
    parent_id: Mapped[int] = mapped_column(
        ForeignKey("inline_date_time_parent_model.id")
    )
    parent: Mapped[InlineDateTimeParentModel] = relationship(back_populates="children")
