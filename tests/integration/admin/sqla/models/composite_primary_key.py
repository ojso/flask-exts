from . import Mapped, db, mapped_column


class CompositePrimaryKeyModel(db.Model):
    __tablename__ = "composite_primary_key_model"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    secondary_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    payload: Mapped[str]
