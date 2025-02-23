from . import db


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    def __init__(self, name=None):
        self.name = name

class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

class UserInfo(db.Model):
    __tablename__ = "user_info"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, nullable=False)
    val = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(
        User,
        backref=db.backref("info", cascade="all, delete-orphan", single_parent=True),
    )

    tag_id = db.Column(db.Integer, db.ForeignKey(Tag.id))
    tag = db.relationship(Tag, backref='user_info')

class UserEmail(db.Model):
    __tablename__ = "user_email"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    verified_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(
        User,
        backref=db.backref("emails", cascade="all, delete-orphan", single_parent=True),
    )
