from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from . import db
# from .user import User  # due to a circular import
from .keyword import Keyword

class UserKeywordAssociation(db.Model):
    __tablename__ = "user_keyword"
    myuser_id = mapped_column(ForeignKey("myuser.id"), primary_key=True)
    keyword_id = mapped_column(ForeignKey("keyword.id"), primary_key=True)
    special_key: Mapped[Optional[str]]

    myuser: Mapped["MyUser"] = relationship(back_populates="user_keyword_associations")
    keyword: Mapped[Keyword] = relationship()

    # Reference to the "keyword" column inside the "Keyword" object.
    keyword_value = association_proxy('keyword', 'keyword')

    def __init__(self, keyword=None, myuser=None, special_key=None):
        self.myuser = myuser
        self.keyword = keyword
        self.special_key = special_key