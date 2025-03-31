from datetime import datetime
from typing import List
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.associationproxy import AssociationProxy
from . import db
from .keyword import Keyword
from .user_keyword import UserKeywordAssociation

class MyUser(db.Model):
    __tablename__="myuser"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    email: Mapped[str]
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )

    user_keyword_associations: Mapped[List["UserKeywordAssociation"]] = relationship(
        back_populates="myuser",
        cascade="all, delete-orphan",
    )

    # association proxy of "user_keyword_associations" collection to "keyword" attribute
    keywords: AssociationProxy[List[Keyword]] = association_proxy(
        "user_keyword_associations",
        "keyword",
        creator=lambda keyword_obj: UserKeywordAssociation(keyword=keyword_obj),
    )

    # Association proxy to association proxy - a list of keywords strings.
    keywords_values = association_proxy('user_keyword_associations', 'keyword_value')


