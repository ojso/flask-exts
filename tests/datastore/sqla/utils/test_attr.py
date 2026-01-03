from sqlalchemy.orm import ColumnProperty
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.orm import CompositeProperty
from sqlalchemy.orm import Relationship
from sqlalchemy.schema import Column
from flask_exts.datastore.sqla.utils import get_model_mapper
from flask_exts.datastore.sqla.utils import is_column
from flask_exts.datastore.sqla.utils import is_relationship
from flask_exts.datastore.sqla.utils.model import is_hybrid
from flask_exts.datastore.sqla.utils import is_hybrid_property
from flask_exts.datastore.sqla.utils import is_association_proxy
from flask_exts.datastore.sqla.utils.model import is_instrumented_attribute
from ..models.demo import Demo


class TestAttr:
    def test_model_attr(self):
        Model = Demo
        for key in [
            "id",
            "name",
            "addresses",
            "full_name",
            "keywords",
        ]:
            attr = getattr(Model, key,None)
            print("is_instrumented_attribute:",is_instrumented_attribute(attr))
            if not is_instrumented_attribute(attr):
                print("is_association_proxy:",is_association_proxy(attr))
            if hasattr(attr, 'parent'):
                print(attr.parent.extension_type)
                # print(attr, type(attr.parent))
        
        return 
        attr = getattr(Model, "id")
        print(attr,type(attr))
        assert is_column(attr) is True
        assert is_column(getattr(Model, "addresses")) is True
        attr = getattr(Model, "full_name_hybrid")
        print(attr, type(attr))
        # assert is_hybrid(attr) is True
