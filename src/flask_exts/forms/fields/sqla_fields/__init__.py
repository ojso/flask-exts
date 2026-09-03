"""
SQLAlchemy field module / SQLAlchemy 字段模块

English summary: This package separates field implementations from the original sqla.py file into smaller modules to improve maintainability and testability.
中文说明：将 sqla.py 中的各个字段类型分离为独立的模块，提高代码的可维护性和可测试性。

Module structure:
- query_fields: query selection fields (QuerySelectField, QuerySelectMultipleField) / 查询选择字段（QuerySelectField, QuerySelectMultipleField）
- inline_fields: inline field types (InlineModelFormListField, InlineModelOneToOneField) / 内联字段（InlineModelFormListField, InlineModelOneToOneField）
- checkbox_fields: checkbox field type (CheckboxListField) / 复选框字段（CheckboxListField）

Backward compatibility note:
It is recommended to keep all exports in sqla.py while pointing to these modular locations / 向后兼容性说明：建议在 sqla.py 中保持所有导出，同时指向新的模块位置。
"""

# English: comment / 从各个子模块导入所有字段
try:
    from .query_fields import QuerySelectField, QuerySelectMultipleField
except ImportError:
    # English: sqla py import / 如果子模块还未完全实现，从 sqla.py 导入
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
