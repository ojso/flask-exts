from . import TEXT, Integer, Mapped, String, db, mapped_column


class StringFieldModel(db.Model):
    __tablename__ = "string_field_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_number: Mapped[int] = mapped_column(Integer, nullable=False)
    optional_string: Mapped[str | None] = mapped_column(String)
    required_string: Mapped[str] = mapped_column(String, nullable=False)
    default_string: Mapped[str] = mapped_column(String, nullable=False, default="")
    optional_text: Mapped[str | None] = mapped_column(TEXT)
    required_text: Mapped[str] = mapped_column(TEXT, nullable=False)
    default_text: Mapped[str] = mapped_column(TEXT, nullable=False, default="")
