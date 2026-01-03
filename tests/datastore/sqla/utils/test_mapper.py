from sqlalchemy.orm import ColumnProperty
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.orm import CompositeProperty
from sqlalchemy.orm import Relationship
from sqlalchemy.schema import Column
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.ext.associationproxy import AssociationProxy
from flask_exts.datastore.sqla.utils import get_model_mapper
from ..models.demo import Demo


class TestMapper:
    def test_model_attrs(self):
        Model = Demo
        mapper = get_model_mapper(Model)

        # table
        assert mapper.local_table == Model.__table__

        assert "point" not in mapper.columns
        assert "point" in mapper.composites

        # columns
        for prop in mapper.columns:
            assert isinstance(prop, Column)
            print(prop, prop.key, type(prop), prop.table)

        # relationships
        for prop in mapper.relationships:
            assert isinstance(prop, RelationshipProperty)
            print(prop, prop.key, type(prop), prop.direction.name, prop.uselist)

        # print("mapper.attrs keys:", list(mapper.attrs.keys()))
        demo_orm_keys = [
            "id",
            "name",
            "first_name",
            "last_name",
            "x",
            "y",
            "start",
            "end",
            "point",
            "kw",
            "addresses",
        ]

        demo_other_keys = ["full_name", "contains", "keywords"]

        assert len(demo_orm_keys) == len(mapper.attrs)
        assert len(demo_orm_keys) + len(demo_other_keys) == len(
            mapper.all_orm_descriptors
        )

        for key in demo_orm_keys:
            assert key in mapper.attrs
            assert key in mapper.all_orm_descriptors

        for key in demo_other_keys:
            assert key not in mapper.attrs
            assert key in mapper.all_orm_descriptors

        mapper_attrs_keys = mapper.attrs.keys()

        for prop in mapper.attrs:
            if isinstance(prop, ColumnProperty):
                assert len(prop.columns) == 1
                col = prop.columns[0]
                assert isinstance(col, Column)
                print(
                    prop, type(prop), col, type(col), col.primary_key, col.foreign_keys
                )
            elif isinstance(prop, RelationshipProperty):
                print(prop, type(prop), prop.direction.name, prop.uselist)
                pass
            elif isinstance(prop, CompositeProperty):
                print(prop, type(prop), prop.attrs)
            else:
                print(prop, "other", type(prop))
                pass

        print("all_orm_descriptors keys:", list(mapper.all_orm_descriptors.keys()))

        for prop, descriptor in mapper.all_orm_descriptors.items():
            print(prop, descriptor, type(descriptor))
            print(isinstance(descriptor, hybrid_property))
            print(isinstance(descriptor, hybrid_method))
            print(isinstance(descriptor, AssociationProxy))
