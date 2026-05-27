import pytest
from flask_exts.admin.sqla.query import Query
from tests.admin.sqla.models.model1 import Model1
from tests.admin.sqla.models.relations import ModelA, ModelB, ModelC




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
    print(query._joinedloads)
    print(query._selectinloads)


def test_count_query():
    manager = Query(ModelA)
    alias_b1 = manager.join_path("first_b")
    stmt = manager.build()
    print(stmt)
    count_stmt = manager.build_count()
    print(count_stmt)


# 使用示例
def test_query():
    # 场景1: [A.a, B.b] 和 [A.b, B.b] 指向同一个 B 的不同实例
    print("=" * 50)
    print("场景1: 多个路径指向同一张表")

    manager = Query(ModelA)

    # 第一次 JOIN: A -> first_b (路径: first_b)
    print('join_path("first_b")')
    alias_b1 = manager.join_path("first_b")
    print(f"第一次 JOIN 返回别名: {alias_b1}")

    # 第二次 JOIN: A -> second_b (路径: second_b)
    # 虽然都指向 TableB，但是是不同的关系，需要不同的别名
    print('join_path("second_b")')
    alias_b2 = manager.join_path("second_b")
    print(f"第二次 JOIN 返回别名: {alias_b2}")

    # 验证是不同的别名
    assert alias_b1 != alias_b2, "应该返回不同的别名"
    print("✓ 正确返回不同别名")

    # 场景2: [A.a, B.b, C.c] 重复部分路径
    print("\n" + "=" * 50)
    print("场景2: 共享前缀路径")

    manager2 = Query(ModelA)

    # 完整路径
    print('join_path(("first_b", "c_items")')
    alias_c1 = manager2.join_path(("first_b", "c_items"))
    print(f"完整路径 first_b -> c_items: {alias_c1}")

    # 再次 JOIN 相同路径，应该复用
    print('join_path(("first_b", "c_items")')
    alias_c2 = manager2.join_path(("first_b", "c_items"))
    print(f"再次 JOIN 相同路径: {alias_c2}")
    assert alias_c1 is alias_c2
    print(f"是否复用: {alias_c1 is alias_c2}")

    # 场景3: 前缀复用
    print("\n" + "=" * 50)
    print("场景3: 前缀复用")

    manager3 = Query(ModelA)

    # 先 JOIN 部分路径
    print('join_path(("first_b",)')
    alias_b = manager3.join_path(("first_b",))
    print(f"先 JOIN first_b: {alias_b}")

    # 再 JOIN 扩展路径，应该复用 first_b
    print('join_path(("first_b", "c_items")')
    alias_c = manager3.join_path(("first_b", "c_items"))
    print(f"再 JOIN first_b -> c_items: {alias_c}")

    # 获取已 JOIN 的别名
    retrieved_b = manager3.get_path_alias(("first_b",))
    print(f"检索 first_b 别名: {retrieved_b}")

    # 在查询中使用
    stmt = manager3.build()
    stmt = stmt.where(manager3.get_column(("first_b", "c_items", "name")) == "test")

    print(f"\n最终 SQL: {stmt}")

    # 场景3-2:
    print("\n" + "=" * 50)
    print("场景3-2: 前缀复用")

    manager32 = Query(ModelA)

    manager32.join_path("first_b.c_items")
    stmt = manager32.build()
    stmt = stmt.where(manager32.get_column(("first_b", "c_items", "name")) == "test")

    print(f"\n最终 SQL: {stmt}")

    # 场景4: 复杂的多路径查询
    print("\n" + "=" * 50)
    print("场景4: 复杂查询示例")

    manager4 = Query(ModelA)

    # 同时 JOIN 多个路径
    print('join_path(("first_b",")')
    alias_b_first = manager4.join_path(("first_b",))
    print('join_path(("second_b",)')
    alias_b_second = manager4.join_path(("second_b",))
    print('join_path(("first_b", "c_items")')
    alias_c_from_first = manager4.join_path(("first_b", "c_items"))
    print('join_path(("second_b", "c_items")')
    alias_c_from_second = manager4.join_path(("second_b", "c_items"))

    # 构建复杂查询
    stmt = manager4.build()
    stmt = stmt.where(
        (manager4.get_column(("first_b", "type")) == "type1")
        & (manager4.get_column(("first_b", "c_items", "value")) > 10)
        | (manager4.get_column(("second_b", "name")) == "special")
    )

    print(f"复杂查询 SQL:\n{stmt}")


def test_column_type():
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
        "enum_type_field",
    ]:
        column_type = Query.get_model_column_type(Model1, key)
        column_type_name = column_type.__class__.__name__
        print(f"Model1.{key} column type: {column_type_name}")
        if column_type_name == "Enum":
            print(f"  Model1.{key} is an Enum with values: {column_type.enums}")
            print(f"  Model1.{key} Enum class: {column_type.enum_class}")
        
