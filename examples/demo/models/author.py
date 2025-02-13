from . import db
from typing import Optional
from typing import List
import enum
from sqlalchemy import sql, cast
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

    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    currency: Mapped[Optional[str]]
    website: Mapped[Optional[str]]
    ip_address: Mapped[Optional[str]]
    timezone: Mapped[Optional[str]]

    dialling_code: Mapped[Optional[int]]
    local_phone_number: Mapped[Optional[str]]
    posts: Mapped[List["Post"]] = relationship(
        foreign_keys="[Post.author_id]",
        back_populates="author",
        cascade="all, delete-orphan",
    )

    featured_post_id = mapped_column(ForeignKey("post.id"))
    featured_post: Mapped["Post"] = relationship(foreign_keys=[featured_post_id])

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
