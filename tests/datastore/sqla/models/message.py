from enum import Enum
from . import db


class MyCat(Enum):
    CAT1 = "Category A"
    CAT2 = "Category B"


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    sender = db.Column(db.String(20))
    recipient = db.Column(db.String(20))
    category = db.Column(db.Enum(MyCat), default=MyCat.CAT1, nullable=False)
