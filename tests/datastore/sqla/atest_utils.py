from flask_exts.datastore.sqla import db
from flask_exts.datastore.sqla.utils import get_primary_key
from flask_exts.datastore.sqla.utils import has_multiple_pks
from flask_exts.datastore.sqla.utils import stmt_delete_model_pk_ids
from flask_exts.datastore.sqla.utils import stmt_select_model_pk_values
from tests.datastore.sqla.models.model_normal import ModelNormal
from tests.datastore.sqla.models.multpk import Multpk


def test_normal(app):
    with app.app_context():
        assert get_primary_key(ModelNormal) == "id"
        assert has_multiple_pks(ModelNormal) is False
        db.reset_models()
        m1 = ModelNormal(id=1, data="first")
        m2 = ModelNormal(id=2, data="second")
        m3 = ModelNormal(id=3, data="third")
        m4 = ModelNormal(id=4, data="fourth")
        db.session.add(m1)
        db.session.add(m2)
        db.session.add(m3)
        db.session.add(m4)
        db.session.commit()

        # select pk values
        stmt = stmt_select_model_pk_values(ModelNormal)
        # print(stmt)
        rows = db.session.execute(stmt).all()
        pk_values = [row[0] for row in rows]
        assert pk_values == [1, 2, 3, 4]

        # delete by pk ids
        ids = [1, 2, 3]
        stmt = stmt_delete_model_pk_ids(ModelNormal, ids)
        # print(stmt)
        result = db.session.execute(stmt)
        db.session.commit()
        # print(result.rowcount)
        assert result.rowcount == 3

        # verify remaining
        stmt = stmt_select_model_pk_values(ModelNormal)
        rows = db.session.execute(stmt).all()
        remain_values = [row[0] for row in rows]
        assert len(remain_values) == 1
        assert remain_values == [4]


def test_multiple_pk(app):
    with app.app_context():
        assert get_primary_key(Multpk) == ("id", "id2")
        assert has_multiple_pks(Multpk) is True
        db.reset_models()
        m1 = Multpk(id=1, id2=1, data="first")
        m2 = Multpk(id=1, id2=2, data="second")
        m3 = Multpk(id=2, id2=1, data="third")
        m4 = Multpk(id=2, id2=2, data="fourth")
        db.session.add(m1)
        db.session.add(m2)
        db.session.add(m3)
        db.session.add(m4)
        db.session.commit()

        # select pk values
        stmt = stmt_select_model_pk_values(Multpk)
        # print(stmt)
        rows = db.session.execute(stmt).all()
        pk_values = [tuple(row) for row in rows]
        assert pk_values == [(1, 1), (1, 2), (2, 1), (2, 2)]

        # delete by pk ids
        ids = [(1, 1), (1, 2)]
        stmt = stmt_delete_model_pk_ids(Multpk, ids)
        # print(stmt)
        # print(stmt.compile(db.engine, compile_kwargs={"literal_binds": True}))
        result = db.session.execute(stmt)
        db.session.commit()
        # print(result.rowcount)
        assert result.rowcount == 2

        # verify remaining
        stmt = stmt_select_model_pk_values(Multpk)
        rows = db.session.execute(stmt).all()
        remain_values = [tuple(row) for row in rows]
        assert len(remain_values) == 2
        assert remain_values == [(2, 1), (2, 2)]
