from . import db


class ModelMultpk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id2 = db.Column(db.String(20), primary_key=True)
    test = db.Column(db.String)
