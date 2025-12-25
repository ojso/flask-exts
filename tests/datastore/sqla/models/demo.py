from enum import Enum
from sqlalchemy.ext.hybrid import hybrid_property
from flask_exts.datastore.sqla import db
from flask_exts.datastore.sqla.orm import Mapped
from flask_exts.datastore.sqla.orm import mapped_column


class Demo(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
