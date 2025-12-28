from . import db
from flask_exts.datastore.sqla.orm import Mapped
from flask_exts.datastore.sqla.orm import mapped_column
from flask_exts.datastore.sqla.orm import relationship
from flask_exts.datastore.sqla.orm import ForeignKey
from flask_exts.datastore.sqla.orm import Table
from flask_exts.datastore.sqla.orm import Column


class MyUser(db.Model):
    __tablename__ = "my_user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class Tag(db.Model):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class UserInfo(db.Model):
    __tablename__ = "user_info"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str]
    val: Mapped[str]
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey(MyUser.id))
    user = db.relationship(
        MyUser,
        backref=db.backref("info", cascade="all, delete-orphan", single_parent=True),
    )

    tag_id = db.Column(db.Integer, db.ForeignKey(Tag.id))
    tag = db.relationship(Tag, backref="user_info")


class UserEmail(db.Model):
    __tablename__ = "user_email"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    verified_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey(MyUser.id))
    user = db.relationship(
        MyUser,
        backref=db.backref("emails", cascade="all, delete-orphan", single_parent=True),
    )
