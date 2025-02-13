from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from . import db


class Tag(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    def __str__(self):
        return "{}".format(self.name)
