from . import db


class PolyParent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test = db.Column(db.String)

    discriminator = db.Column("type", db.String(50))
    __mapper_args__ = {"polymorphic_on": discriminator}


class ChildPoly(PolyParent):
    __tablename__ = "children"
    __mapper_args__ = {"polymorphic_identity": "child"}

    id = db.Column(db.ForeignKey(PolyParent.id), primary_key=True)
    name = db.Column(db.String(100))


class Child2(PolyParent):
    __mapper_args__ = {"polymorphic_identity": "child2"}
    name = db.Column(db.String(100))

class ChildCrete(PolyParent):
    __mapper_args__ = {"concrete": True,"polymorphic_identity": "child3"}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    test = db.Column(db.String)

class ChildMultpk(PolyParent):
    __mapper_args__ = {"concrete": True,"polymorphic_identity": "child4"}
    id = db.Column(db.Integer, primary_key=True)
    id2 = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    test = db.Column(db.String)