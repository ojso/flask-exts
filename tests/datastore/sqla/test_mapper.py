from sqlalchemy.orm import ColumnProperty
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.orm import CompositeProperty
from sqlalchemy.orm import Relationship
from sqlalchemy.schema import Column
from flask_exts.datastore.sqla.utils import get_model_mapper
from .models.demo import Demo


class TestMapper:
    def test_model_attrs(self):
        Model = Demo
        mapper = get_model_mapper(Model)
        # table
        assert mapper.local_table == Model.__table__
        # columns
        for p in mapper.columns:
            assert isinstance(p, Column)
            # print(p, p.key, type(p), p.table)
        # relationships
        for p in mapper.relationships:
            assert isinstance(p, RelationshipProperty)
            # print(p, p.key, type(p), p.direction.name,p.uselist)
        # attrs
        for p in mapper.attrs:
            # print(p, p.key, type(p))
            if isinstance(p, ColumnProperty):
                if len(p.columns) == 1:
                    col = p.columns[0]
                    assert isinstance(col, Column)
                    print(col, type(col), col.primary_key, col.foreign_keys)
            elif isinstance(p, RelationshipProperty):
                print(p, type(p), p.direction.name, p.uselist)
                pass
            elif isinstance(p, Relationship):
                print(p, type(p), p.direction.name, p.uselist)
                pass
            elif isinstance(p, CompositeProperty):
                print(p, type(p), p.columns)
                pass
            else:
                print(p, "other", type(p))
                pass
