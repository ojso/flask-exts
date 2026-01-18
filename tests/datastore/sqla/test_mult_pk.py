from . import db
from . import select
from . import selectinload
from . models.multpk import Multpk


def test_mappers():
    for mapper in db.Model.registry.mappers:
        print(mapper.class_.__name__, mapper.local_table)


def test_create_table(app):
    with app.app_context():
        db.create_all()
        mp11 = Multpk(id=1, id2=1, data="data1")
        mp12 = Multpk(id=1, id2=2, data="data2")
        mp21 = Multpk(id=2, id2=1, data="data3")
        db.session.add_all(
            [
                mp11,
                mp12,
                mp21,
            ]
        )
        db.session.commit()
        stmt = select(Multpk)
        print(stmt)
        mps = db.session.execute(stmt).scalars()
        for mp in mps:
            assert isinstance(mp, Multpk)
            print(mp.id, mp.id2, mp.data)