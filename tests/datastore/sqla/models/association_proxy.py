from typing import Final
from typing import List
from . import db
from . import Mapped
from . import mapped_column
from . import ForeignKey
from . import relationship
from . import Table
from . import Column
from . import Integer
from . import String
from . import association_proxy
from . import AssociationProxy

# see https://docs.sqlalchemy.org/en/20/orm/extensions/associationproxy.html


class Keyword(db.Model):
    __tablename__ = "keyword"
    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column(String(64))

    def __init__(self, keyword: str):
        self.keyword = keyword


class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    kw: Mapped[List[Keyword]] = relationship(secondary=lambda: user_keyword_table)

    def __init__(self, name: str):
        self.name = name

    # proxy the 'keyword' attribute from the 'kw' relationship
    keywords: AssociationProxy[List[str]] = association_proxy("kw", "keyword")


user_keyword_table: Final[Table] = Table(
    "user_keyword",
    db.Model.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("keyword_id", Integer, ForeignKey("keyword.id"), primary_key=True),
)
