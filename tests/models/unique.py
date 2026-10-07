from . import Mapped, db, mapped_column


class UniqueModel(db.Model):
    __tablename__ = "unique_model"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    value: Mapped[str]
