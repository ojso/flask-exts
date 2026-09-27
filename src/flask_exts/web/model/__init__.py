"""Admin model view package.

This package provides the model-management layer used by the admin views,
including list/detail forms, filters, sorting, pagination, and CRUD operations.

The public surface is arranged as follows:

- ModelView: primary admin view implementation.
- BaseModelView: shared base class composed from all mixins.
- core/: column, sorting, pagination, value, and form helpers.
- operations/: read, create, update, delete, and export operations.
- Mixin classes: action, row-action, and filtering helpers.

Example:
    ```python
    from flask_exts.web.model import ModelView

    class UserAdmin(ModelView):
        column_list = ['id', 'username', 'email', 'created_at']
        column_sortable_list = ['username', 'created_at']

    admin.register_view(UserAdmin, User)
    ```
"""

from .view import ModelView
from .base import BaseModelView

from .core import (
    ColumnsMixin,
    SortingMixin,
    PaginationMixin,
    ValuesMixin,
    FormsMixin,
)

from .operations import (
    ReadOperationsMixin,
    CreateOperationsMixin,
    UpdateOperationsMixin,
    DeleteOperationsMixin,
    ExportOperationsMixin,
)

from .actions_mixin import ActionsMixin
from .row_actions import RowActionMixin
from .filter_mixin import FilterMixin

__all__ = [
    'ModelView',
    'BaseModelView',
    'ColumnsMixin',
    'SortingMixin',
    'PaginationMixin',
    'ValuesMixin',
    'FormsMixin',
    'ReadOperationsMixin',
    'CreateOperationsMixin',
    'UpdateOperationsMixin',
    'DeleteOperationsMixin',
    'ExportOperationsMixin',
    'ActionsMixin',
    'RowActionMixin',
    'FilterMixin',
]
