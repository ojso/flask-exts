"""
查询字段

包含 QuerySelectField 和 QuerySelectMultipleField 等基于查询的字段类型。

这些字段用于在表单中选择 SQLAlchemy ORM 对象。
"""

# 注意：实际的字段实现应从 sqla.py 中提取到这里
# 此文件是字段模块化的占位符

__all__ = [
    'QuerySelectField',
    'QuerySelectMultipleField',
]
