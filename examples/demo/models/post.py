from . import db
from datetime import datetime
from typing import Optional
from typing import List
import enum
from sqlalchemy import sql, cast
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.ext.hybrid import hybrid_property

AVAILABLE_USER_TYPES = [
    ("admin", "Admin"),
    ("content-writer", "Content writer"),
    ("editor", "Editor"),
    ("regular-author", "Regular author"),
]


class EnumChoices(enum.Enum):
    first = 1
    second = 2


# Create models
class Author(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    # we can specify a list of available choices later on
    type: Mapped[str]

    # fixed choices can be handled in a number of different ways:
    enum_choice_field: Mapped[Optional[EnumChoices]]

    first_name: Mapped[str]
    last_name: Mapped[str]

    email: Mapped[str] = mapped_column(unique=True,nullable=False)
    currency: Mapped[Optional[str]]
    website: Mapped[Optional[str]]
    ip_address: Mapped[Optional[str]]
    timezone: Mapped[Optional[str]]

    dialling_code: Mapped[int]
    local_phone_number: Mapped[str]
    posts: Mapped[List["Post"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )

    @hybrid_property
    def phone_number(self):
        if self.dialling_code and self.local_phone_number:
            number = str(self.local_phone_number)
            return "+{} ({}) {} {} {}".format(
                self.dialling_code, number[0], number[1:3], number[3:6], number[6::]
            )
        return

    @phone_number.expression
    def phone_number(cls):
        return sql.operators.ColumnOperators.concat(
            cast(cls.dialling_code, db.String), cls.local_phone_number
        )

    def __str__(self):
        return "{}, {}".format(self.last_name, self.first_name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())


class AssociationPostTag(db.Model):
    __tablename__ = "post_tag"
    post_id = Column(ForeignKey("post.id"), primary_key=True)
    tag_id = Column(ForeignKey("tag.id"), primary_key=True)
    post: Mapped["Post"] = relationship(back_populates="tags")
    tag: Mapped["Tag"] = relationship(back_populates="posts")


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    text: Mapped[str]
    color: Mapped[str]
    date: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id"))
    author: Mapped["Author"] = relationship(back_populates="posts")
    tags: Mapped[List["AssociationPostTag"]] = relationship(back_populates="post")

    def __str__(self):
        return "{}".format(self.title)


class Tag(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    posts: Mapped[List["AssociationPostTag"]] = relationship(back_populates="tag")

    def __str__(self):
        return "{}".format(self.name)



