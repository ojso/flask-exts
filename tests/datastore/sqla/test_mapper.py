from sqlalchemy import inspect

from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.properties import RelationshipProperty
from sqlalchemy.orm.properties import CompositeProperty
from sqlalchemy.orm.properties import SynonymProperty

from sqlalchemy.orm import InspectionAttr
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.orm import MapperProperty
from sqlalchemy.orm import InstrumentedAttribute

from sqlalchemy.orm import Relationship
from sqlalchemy.orm import synonym
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.ext.associationproxy import AssociationProxy
from sqlalchemy.schema import Column

from . import db
from .models.demo import Demo


class TestMapper:
    def test_mappers(self):
        for mapper in db.Model.registry.mappers:
            print(mapper.class_.__name__, mapper.local_table)

    def test_inspect(self):
        Model = Demo
        mapper = inspect(Model)

        # table
        assert mapper.local_table == Model.__table__

        # all_orm_descriptors
        print("===== all_orm_descriptors =====")
        print("all_orm_descriptors.keys:", list(mapper.all_orm_descriptors.keys()))
        print("columns.keys:", list(mapper.column_attrs.keys()))
        print("relationships.keys:", list(mapper.relationships.keys()))
        print("composites.keys:", list(mapper.composites.keys()))
        print("synonyms.keys:", list(mapper.synonyms.keys()))

        others = (
            set(mapper.all_orm_descriptors.keys())
            .difference(set(mapper.column_attrs.keys()))
            .difference(set(mapper.relationships.keys()))
            .difference(set(mapper.composites.keys()))
            .difference(set(mapper.synonyms.keys()))
        )

        print("other:", list(others))
        for k in list(others):
            descriptor = mapper.all_orm_descriptors[k]
            if isinstance(descriptor, AssociationProxy):
                print(
                    k,
                    descriptor,
                    type(descriptor),
                    descriptor.target_collection,
                    descriptor.value_attr,
                )
                pp = getattr(Model, k)
                print(pp, type(pp))
                print(pp.parent, type(pp.parent))
                pass
            elif isinstance(descriptor, hybrid_property):
                pass
            elif isinstance(descriptor, hybrid_method):
                pass
            else:
                raise Exception(f"unknown {descriptor}.type {type(descriptor)}")
        return
        for prop, descriptor in mapper.all_orm_descriptors.items():
            assert isinstance(descriptor, InspectionAttr) and descriptor.is_attribute
            if isinstance(descriptor, QueryableAttribute):
                # print(key, descriptor, type(descriptor),type(descriptor.property))
                assert isinstance(descriptor.property, MapperProperty)
                if isinstance(descriptor, InstrumentedAttribute):
                    assert isinstance(
                        descriptor.property, ColumnProperty
                    ) or isinstance(descriptor.property, RelationshipProperty)
                else:
                    if isinstance(descriptor.property, CompositeProperty):
                        pass
                    elif isinstance(descriptor.property, ColumnProperty):
                        # is SynonymProperty
                        pass
                    else:
                        print(
                            prop,
                            descriptor,
                            type(descriptor),
                            type(descriptor.property),
                        )
            else:
                print(descriptor, type(descriptor))
                if isinstance(descriptor, AssociationProxy):
                    pass
                elif isinstance(descriptor, hybrid_property):
                    pass
                elif isinstance(descriptor, hybrid_method):
                    pass
                else:
                    raise Exception(f"unknown {prop}.type {type(descriptor)}")

        assert "point" not in mapper.columns
        assert "point" in mapper.composites

        # columns
        print("===== columns =====")
        for col in mapper.columns:
            assert isinstance(col, Column)
            print(col, col.key, col.table)

        print("===== column_attrs =====")
        for p in mapper.column_attrs:
            assert isinstance(p, ColumnProperty)
            print(p, p.key, type(p))

        # relationships
        print("===== relationships =====")
        for p in mapper.relationships:
            assert isinstance(p, RelationshipProperty)
            print(p, p.key, p.direction.name, p.uselist)

        # composites
        print("===== composites =====")
        for p in mapper.composites:
            assert isinstance(p, CompositeProperty)
            print(p, p.key, p.attrs)

        # synonyms
        print("===== synonyms =====")
        for p in mapper.synonyms:
            assert isinstance(p, SynonymProperty)
            print(p, p.key)

        # attrs
        print("===== attrs =====")

        for prop in mapper.attrs:
            if isinstance(prop, ColumnProperty):
                assert len(prop.columns) == 1
                prop = prop.columns[0]
                assert isinstance(prop, Column)
                print(
                    prop,
                    type(prop),
                    prop,
                    type(prop),
                    prop.primary_key,
                    prop.foreign_keys,
                )
            elif isinstance(prop, RelationshipProperty):
                print(prop, type(prop), prop.direction.name, prop.uselist)
                pass
            elif isinstance(prop, CompositeProperty):
                print(prop, type(prop), prop.attrs)
            elif isinstance(prop, SynonymProperty):
                print(prop, type(prop))
            else:
                raise Exception(f"unknown type{type(prop)}")

    def test_model_attrs(self):
        Model = Demo
        mapper = inspect(Model)

        for attr_name in mapper.all_orm_descriptors.keys():
            attr = getattr(Model, attr_name)
            print(attr, type(attr))
            continue
            if hasattr(attr, "property") and isinstance(attr.property, MapperProperty):
                prop = attr.property
                if isinstance(prop, ColumnProperty):
                    print(
                        f"ColumnProperty: {attr_name}, columns: {[col.name for col in prop.columns]}"
                    )
                elif isinstance(prop, RelationshipProperty):
                    print(
                        f"RelationshipProperty: {attr_name}, direction: {prop.direction.name}, uselist: {prop.uselist}"
                    )
                elif isinstance(prop, CompositeProperty):
                    print(f"CompositeProperty: {attr_name}, attrs: {prop.attrs}")
                elif isinstance(prop, SynonymProperty):
                    print(f"SynonymProperty: {attr_name}, synonym for: {prop.name}")
                else:
                    print(f"Unknown MapperProperty type for attribute: {attr_name}")
            else:
                # Not a mapped property
                print(f"Non-mapped attribute: {attr_name}")
                pass
