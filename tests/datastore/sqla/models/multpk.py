from .. import db
from .. import Mapped
from .. import mapped_column


class Multpk(db.Model):
    __tablename__ = "multpk"
    id: Mapped[int] = mapped_column(primary_key=True)
    id2: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[str]
