from . import db
from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from .tag import Tag
from .post_tag import post_tag_table


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    text: Mapped[str]
    color: Mapped[str]
    date: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id"))
    author: Mapped["Author"] = relationship(
        foreign_keys=[author_id], back_populates="posts"
    )
    tags: Mapped[List["Tag"]] = relationship(secondary=post_tag_table)

    def __str__(self):
        return "{}".format(self.title)
