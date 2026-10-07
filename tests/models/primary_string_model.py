from . import Mapped, db, mapped_column


class PrimaryStringModel(db.Model):
    __tablename__ = "primary_string_model"

    id: Mapped[str] = mapped_column(primary_key=True)
    test: Mapped[str]
