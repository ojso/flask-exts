from . import db
from . import Mapped
from . import mapped_column


class SimpleModel(db.Model):
    __tablename__ = "simple_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
