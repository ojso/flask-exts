from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from . import db


class Keyword(db.Model):
    __tablename__ = "keyword"
    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str]

    def __init__(self, keyword: str):
        self.keyword = keyword

    def __repr__(self):
        return "Keyword(%s)" % repr(self.keyword)
