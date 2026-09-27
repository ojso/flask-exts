"""SQLAlchemy field modules.

This package keeps the original SQLAlchemy field implementations separated into
smaller modules to improve maintainability and testability.

The package is organized around the following submodules:

- query_fields: query selection fields such as QuerySelectField and
  QuerySelectMultipleField.
- inline_fields: inline form field helpers such as
  InlineModelFormListField and InlineModelOneToOneField.
- checkbox_fields: checkbox field helpers such as CheckboxListField.

Backward compatibility is preserved by keeping the public exports in the
higher-level SQLAlchemy form module while delegating implementations here.
"""

try:
    from .query_fields import QuerySelectField, QuerySelectMultipleField
except ImportError:
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
    'CheckboxListField',
    'InlineModelFormListField',
    'InlineModelOneToOneField',
    'QuerySelectField',
    'QuerySelectMultipleField',
]
