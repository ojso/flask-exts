from . import Mapped, db, mapped_column


class UniqueValidationModel(db.Model):
    __tablename__ = "unique_validation_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    message: Mapped[str]
