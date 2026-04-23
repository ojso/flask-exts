import pytest
from flask_exts.datastore.sqla.utils.attr import get_field_with_path
from tests.datastore.sqla.models.model1 import Model1


def test_get_field_with_path():

    # Test simple column access
    attr, joins = get_field_with_path(Model1, "test1")
    # print(attr, [str(join) for join in joins])
    assert attr.key == "test1"
    assert len(joins) == 0

    # Test relationship access
    attr, joins = get_field_with_path(Model1, "model2")
    # print(attr, [str(join) for join in joins])
    assert attr.key == "model2"
    assert len(joins) == 1
    assert joins[0].key == "model2"

    # Test nested relationship access
    attr, joins = get_field_with_path(Model1, "model2.string_field")
    # print(attr, [str(join) for join in joins])
    assert attr.key == "string_field"
    assert len(joins) == 1
    assert joins[0].key == "model2"

    attr, joins = get_field_with_path(Model1, "model2.model3.val")
    # print(attr, [str(join) for join in joins])
    assert attr.key == "val"
    assert len(joins) == 2
    assert joins[0].key == "model2"
    assert joins[1].key == "model3"

    # Test invalid path
    with pytest.raises(AttributeError, match="has no attribute"):
        get_field_with_path(Model1, "name.invalid")
