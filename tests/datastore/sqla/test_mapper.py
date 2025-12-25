from sqlalchemy.orm import ColumnProperty, RelationshipProperty
from flask_exts.datastore.sqla.utils import get_model_mapper
from .models.demo import Demo


class TestMapper:
    def test_attrs(self):
        mapper = get_model_mapper(Demo)
        # table
        assert mapper.local_table == Demo.__table__
        # attrs
        print("\n" + "=" * 30)
        for p in mapper.attrs:
            print(p, p.key, type(p))
        print("\n" + "=" * 30)
        for p in mapper.attrs:
            if isinstance(p, ColumnProperty):
                print(p, "column", len(p.columns))
                for c in p.columns:
                    print(c, c.table)
            elif isinstance(p, RelationshipProperty):
                print(p, "relation", p.direction.name)
            else:
                print(p, type(p))
