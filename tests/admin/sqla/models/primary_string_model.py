from . import db
from . import Mapped
from . import mapped_column


class ModelPrimaryString(db.Model):
    __tablename__ = "model_primary_string"

    id: Mapped[str] = mapped_column(primary_key=True)
    test: Mapped[str]