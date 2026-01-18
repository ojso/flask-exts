from . import db
from . import select
from . import selectinload
from .models.association_proxy import User, Keyword


def test_mappers():
    for mapper in db.Model.registry.mappers:
        print(mapper.class_.__name__, mapper.local_table)


def test_create_table(app):
    with app.app_context():
        db.create_all()
        kw1 = Keyword(keyword="Python")
        kw2 = Keyword(keyword="SQLAlchemy")
        kw3 = Keyword(keyword="Flask")
        u1 = User(name="alice")
        u2 = User(name="bob")
        db.session.add_all(
            [
                kw1,
                kw2,
                u1,
                u2,
            ]
        )
        u1.kw.append(kw1)
        u1.kw.append(kw2)
        u2.kw.append(kw3)
        db.session.commit()
        stmt = select(User).options(selectinload(User.kw))
        print(stmt)
        users = db.session.execute(stmt).scalars()
        for u in users:
            assert isinstance(u, User)
            # print(u.name, u.kw)
            print(u.name, u.keywords)
