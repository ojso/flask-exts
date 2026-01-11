from . import db
from . import Mapped
from . import mapped_column
from . import ForeignKey
from . import relationship

class MyUser(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class Tag(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class UserInfo(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str]
    val: Mapped[str]
    user_id = mapped_column(ForeignKey("my_user.id"))
    user: Mapped[MyUser] = relationship(back_populates="info",cascade="all, delete-orphan", single_parent=True)
    tag_id = mapped_column(ForeignKey("tag.id"))
    tag:Mapped[Tag] = relationship(backref="user_info")


class UserEmail(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email:Mapped[str]=mapped_column(nullable=False, unique=True)
    verified_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey(MyUser.id))
    user = db.relationship(
        MyUser,
        backref=db.backref("emails", cascade="all, delete-orphan", single_parent=True),
    )
