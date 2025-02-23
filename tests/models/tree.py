from . import db


class Tree(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("tree.id"))
    parent = db.relationship("Tree", remote_side=[id], backref="children")
