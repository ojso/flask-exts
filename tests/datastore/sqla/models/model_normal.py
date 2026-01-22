from .. import db
from .. import Mapped
from .. import mapped_column


class ModelNormal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[str]


