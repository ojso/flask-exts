from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import db
from .post_tag import post_tag_table
from .tag import Tag

if TYPE_CHECKING:
    from .author import Author


class Post(db.Model):
    __tablename__ = "post"

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
    tags: Mapped[list["Tag"]] = relationship(secondary=post_tag_table)

    def __str__(self):
        return "{}".format(self.title)
