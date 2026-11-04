from . import Mapped, db, mapped_column


class StringPrimaryKeyModel(db.Model):
    __tablename__ = "string_primary_key_model"

    id: Mapped[str] = mapped_column(primary_key=True, autoincrement=False)
    value: Mapped[str]
