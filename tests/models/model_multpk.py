from . import db
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class ModelMultpk(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    id2: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[str]


