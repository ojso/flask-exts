import enum
from datetime import date, datetime, time

from . import (
    TEXT,
    ForeignKey,
    Mapped,
    String,
    db,
    mapped_column,
    relationship,
)


class AdminEnumChoice(enum.Enum):
    first = 1
    second = 2


class AdminTestModel(db.Model):
    __tablename__ = "admin_test_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str | None]
    short_text: Mapped[str | None] = mapped_column(String(20))
    long_text: Mapped[str | None] = mapped_column(TEXT)
    default_text = mapped_column(String(20), nullable=False, default="")
    integer_value: Mapped[int | None]
    float_value: Mapped[float | None]
    boolean_value: Mapped[bool | None]
    date_value: Mapped[date | None]
    time_value: Mapped[time | None]
    datetime_value: Mapped[datetime | None]
    email: Mapped[str | None]
    enum_choice: Mapped[AdminEnumChoice | None]
    choice_value: Mapped[str | None]
    related_records: Mapped[list["RelatedAdminTestModel"]] = relationship(
        back_populates="admin_record"
    )

    def __str__(self):
        return str(self.name)


class RelatedAdminTestModel(db.Model):
    __tablename__ = "related_admin_test_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    optional_string: Mapped[str]

    admin_record_id = mapped_column(ForeignKey("admin_test_model.id"))
    nested_record_id = mapped_column(ForeignKey("nested_admin_test_model.id"))

    admin_record: Mapped[AdminTestModel] = relationship(
        back_populates="related_records"
    )
    nested_record: Mapped["NestedAdminTestModel"] = relationship(
        back_populates="related_records"
    )


class NestedAdminTestModel(db.Model):
    __tablename__ = "nested_admin_test_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str]
    related_records: Mapped[list["RelatedAdminTestModel"]] = relationship(
        back_populates="nested_record"
    )
