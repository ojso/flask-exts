from flask_exts.datastore.sqla.utils.attr import get_field_with_path
from tests.datastore.sqla.models.model1 import Model1


def test_get_field_with_path():

    # Test simple column access
    attr, joins = get_field_with_path(Model1, "test1")
    # print(attr, joins)
    assert attr.key == "test1"
    assert joins == []

    # Test relationship access
    attr, joins = get_field_with_path(Model1, "model2")
    print(attr, joins)
    assert attr.key == "model2"
    assert len(joins) == 1
    assert joins[0].key == "model2"

    # Test nested relationship access
    attr, joins = get_field_with_path(Model1, "model2.string_field")
    print(attr, joins)
    print(attr.key)
    assert attr.key == "string_field"
    assert len(joins) == 1
    assert joins[0].key == "model2"
    return

    # Test invalid path (column followed by more segments)
    try:
        get_field_with_path(Model1, "invalid")
        assert False, "Expected ValueError for invalid path"
    except ValueError as e:
        assert str(e) == "Column 'name' cannot be followed by further path segments."
