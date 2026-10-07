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
    from flask_exts.admin.model import ModelView

    class UserAdmin(ModelView):
        column_list = ['id', 'username', 'email', 'created_at']
        column_sortable_list = ['username', 'created_at']

    admin.register_view(UserAdmin, User)
    ```
"""

from .actions_mixin import ActionsMixin
from .base import BaseModelView
from .core import (
    ColumnsMixin,
    FormsMixin,
    PaginationMixin,
    SortingMixin,
    ValuesMixin,
)
from .filter_mixin import FilterMixin
from .operations import (
    CreateOperationsMixin,
    DeleteOperationsMixin,
    ExportOperationsMixin,
    ReadOperationsMixin,
    UpdateOperationsMixin,
)
from .row_actions import RowActionMixin
from .view import ModelView

__all__ = [
    "ActionsMixin",
    "BaseModelView",
    "ColumnsMixin",
    "CreateOperationsMixin",
    "DeleteOperationsMixin",
    "ExportOperationsMixin",
    "FilterMixin",
    "FormsMixin",
    "ModelView",
    "PaginationMixin",
    "ReadOperationsMixin",
    "RowActionMixin",
    "SortingMixin",
    "UpdateOperationsMixin",
    "ValuesMixin",
]
