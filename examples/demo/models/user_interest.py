from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from flask_exts.userstore.sqla.models.user import User

from . import db


class UserInterest(db.Model):
    """One free-text interest record per user."""

    __tablename__ = "user_interest"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Unique so a user owns at most one interest row.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    content: Mapped[str]

    # One-way relationship: the reverse attribute would live on the library
    # User model, which this demo does not extend.
    user: Mapped["User"] = relationship("User")

    def __str__(self):
        return self.content
