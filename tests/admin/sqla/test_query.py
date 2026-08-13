import pytest
from flask_exts.admin.sqla.query import Query
from tests.models.demo import Model1
from tests.models.relations import ModelA, ModelB, ModelC


def test_get_field_with_path():

    # Test simple column access
    attr, joins = Query.get_field_with_path(Model1, "test1")
    # print(attr, [str(join) for join in joins])
    assert attr.key == "test1"
    assert len(joins) == 0

    # Test relationship access
    attr, joins = Query.get_field_with_path(Model1, "model2")
    # print(attr, [str(join) for join in joins])
    assert attr.key == "model2"
    assert len(joins) == 1
    assert joins[0].key == "model2"

    # Test nested relationship access
    attr, joins = Query.get_field_with_path(Model1, "model2.string_field")
    # print(attr, [str(join) for join in joins])
    assert attr.key == "string_field"
    assert len(joins) == 1
    assert joins[0].key == "model2"

    attr, joins = Query.get_field_with_path(Model1, "model2.model3.val")
    # print(attr, [str(join) for join in joins])
    assert attr.key == "val"
    assert len(joins) == 2
    assert joins[0].key == "model2"
    assert joins[1].key == "model3"

    # Test invalid path
    with pytest.raises(AttributeError, match="has no attribute"):
        Query.get_field_with_path(Model1, "name.invalid")


def test_eager_load():
    query = Query(ModelB)
    query.add_eager_loads(["a_first", "x"])
    # print(query._joinedloads)
    # print(query._selectinloads)


def test_count_query():
    manager = Query(ModelA)
    alias_b1 = manager.join_path("first_b")
    stmt = manager.build()
    # print(stmt)
    count_stmt = manager.build_count()
    # print(count_stmt)


def test_join_path():
    manager = Query(ModelA)

    # First JOIN: A -> first_b (path: first_b)
    # print('join_path("first_b")')
    alias_b1 = manager.join_path("first_b")
    # print(f"First JOIN returned alias: {alias_b1}")

    # Second JOIN: A -> second_b (path: second_b)
    # Although both point to TableB, they are different relationships and need different aliases
    # print('join_path("second_b")')
    alias_b2 = manager.join_path("second_b")
    # print(f"Second JOIN returned alias: {alias_b2}")

    # Verify they are different aliases
    assert alias_b1 != alias_b2, "Should return different aliases"
    # print("✓ Correctly returned different aliases")

    # Scenario 2: [A.a, B.b, C.c] repeated partial paths
    # print("\n" + "=" * 50)
    # print("Scenario 2: Shared prefix paths")

    manager2 = Query(ModelA)

    # Full path
    # print('join_path(("first_b", "c_items")')
    alias_c1 = manager2.join_path(("first_b", "c_items"))
    # print(f"Full path first_b -> c_items: {alias_c1}")

    # JOIN the same path again, should reuse
    # print('join_path(("first_b", "c_items")')
    alias_c2 = manager2.join_path(("first_b", "c_items"))
    # print(f"JOIN same path again: {alias_c2}")
    assert alias_c1 is alias_c2
    # print(f"Is reused: {alias_c1 is alias_c2}")

    # Scenario 3: Prefix reuse
    # print("\n" + "=" * 50)
    # print("Scenario 3: Prefix reuse")

    manager3 = Query(ModelA)

    # First JOIN partial path
    # print('join_path(("first_b",)')
    alias_b = manager3.join_path(("first_b",))
    # print(f"First JOIN first_b: {alias_b}")

    # Then JOIN extended path, should reuse first_b
    # print('join_path(("first_b", "c_items")')
    alias_c = manager3.join_path(("first_b", "c_items"))
    # print(f"Then JOIN first_b -> c_items: {alias_c}")

    # Get already JOINed alias
    retrieved_b = manager3.get_path_alias(("first_b",))
    # print(f"Retrieved first_b alias: {retrieved_b}")

    # Use in query
    stmt = manager3.build()
    stmt = stmt.where(manager3.get_column(("first_b", "c_items", "name")) == "test")

    # print(f"\nFinal SQL: {stmt}")

    # Scenario 3-2:
    # print("\n" + "=" * 50)
    # print("Scenario 3-2: Prefix reuse")

    manager32 = Query(ModelA)

    manager32.join_path("first_b.c_items")
    stmt = manager32.build()
    stmt = stmt.where(manager32.get_column(("first_b", "c_items", "name")) == "test")

    # print(f"\nFinal SQL: {stmt}")

    # Scenario 4: Complex multi-path query

    manager4 = Query(ModelA)

    # JOIN multiple paths simultaneously
    alias_b_first = manager4.join_path(("first_b",))
    alias_b_second = manager4.join_path(("second_b",))
    alias_c_from_first = manager4.join_path(("first_b", "c_items"))
    alias_c_from_second = manager4.join_path(("second_b", "c_items"))

    # Build complex query
    stmt = manager4.build()
    stmt = stmt.where(
        (manager4.get_column(("first_b", "type")) == "type1")
        & (manager4.get_column(("first_b", "c_items", "value")) > 10)
        | (manager4.get_column(("second_b", "name")) == "special")
    )

    # print(f"Complex query SQL:\n{stmt}")


def test_get_column_type():
    for key in [
        "id",
        "test1",
        "test2",
        "test3",
        "test4",
        "bool_field",
        "date_field",
        "time_field",
        "datetime_field",
        "email_field",
        "enum_field",
    ]:
        column_type = Query.get_model_column_type(Model1, key)
        column_type_name = column_type.__class__.__name__
        # print(f"Model1.{key} column type: {column_type_name}")
        assert column_type is not None, f"Column type for Model1.{key} should not be None"
        if column_type_name == "Enum":
            # print(f"  Model1.{key} is an Enum with values: {column_type.enums}")
            # print(f"  Model1.{key} Enum class: {column_type.enum_class}")
            pass
