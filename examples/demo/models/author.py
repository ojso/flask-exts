import enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, cast, sql
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import db

if TYPE_CHECKING:
    from .post import Post

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
    __tablename__ = "author"
    id: Mapped[int] = mapped_column(primary_key=True)
    # we can specify a list of available choices later on
    type: Mapped[str]

    # fixed choices can be handled in a number of different ways:
    enum_choice_field: Mapped[EnumChoices | None]

    first_name: Mapped[str]
    last_name: Mapped[str]

    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    currency: Mapped[str | None]
    website: Mapped[str | None]
    ip_address: Mapped[str | None]
    timezone: Mapped[str | None]

    dialling_code: Mapped[int | None]
    local_phone_number: Mapped[str | None]
    posts: Mapped[list["Post"]] = relationship(  # noqa: F821
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
            cast(cls.dialling_code, String), cls.local_phone_number
        )

    def __str__(self):
        return "{}, {}".format(self.last_name, self.first_name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())
