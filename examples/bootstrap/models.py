from enum import Enum
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from flask_exts.datastore.sqla import db


class MyCategory(Enum):
    CAT1 = "Category 1"
    CAT2 = "Category 2"


class Message(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(nullable=False)
    author: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[MyCategory] = mapped_column(default=MyCategory.CAT1, nullable=False)
    draft: Mapped[bool] = mapped_column(default=False, nullable=False)
    create_time: Mapped[int] = mapped_column(nullable=False, unique=True)

