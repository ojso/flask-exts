"""
SQLAlchemy 字段模块

将 sqla.py 中的各个字段类型分离为独立的模块，提高代码的可维护性和可测试性。

模块结构：
- query_fields: 查询选择字段（QuerySelectField, QuerySelectMultipleField）
- inline_fields: 内联字段（InlineModelFormListField, InlineModelOneToOneField）
- checkbox_fields: 复选框字段（CheckboxListField）

向后兼容性说明：
建议在 sqla.py 中保持所有导出，同时指向新的模块位置。
"""

# 从各个子模块导入所有字段
try:
    from .query_fields import QuerySelectField, QuerySelectMultipleField
except ImportError:
    # 如果子模块还未完全实现，从 sqla.py 导入
    pass

try:
    from .inline_fields import InlineModelFormListField, InlineModelOneToOneField
except ImportError:
    pass

try:
    from .checkbox_fields import CheckboxListField
except ImportError:
    pass

__all__ = [
    'QuerySelectField',
    'QuerySelectMultipleField',
    'CheckboxListField',
    'InlineModelFormListField',
    'InlineModelOneToOneField',
]
