"""
基础 ModelView 类

将所有核心功能混入和操作混入组合成单个基础类。
这个类仍然是抽象的，特定的后端实现（SQLAlchemy, Peewee 等）
应该继承这个类并实现抽象方法。
"""

from ..view import View
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
from .rowaction_mixin import RowActionMixin
from .filter_mixin import FilterMixin
from .form_mixin import FormMixin


class BaseModelView(
    View,
    ColumnsMixin,
    SortingMixin,
    PaginationMixin,
    ValuesMixin,
    FormsMixin,
    ReadOperationsMixin,
    CreateOperationsMixin,
    UpdateOperationsMixin,
    DeleteOperationsMixin,
    ExportOperationsMixin,
    ActionsMixin,
    RowActionMixin,
    FilterMixin,
    FormMixin,
):
    """
    Admin ModelView 基础类。

    组合所有核心功能模块和操作模块，提供完整的 Admin 界面。

    这个类是抽象的。特定的后端实现应该继承这个类并实现以下抽象方法：

    - scaffold_list_columns()：从模型获取列列表
    - scaffold_sortable_columns()：从模型获取可排序列列表
    - scaffold_form()：从模型生成表单类
    - scaffold_list_form()：从模型生成列表编辑表单
    - get_list()：获取分页数据列表
    - get_one()：按 ID 获取单个模型
    - get_pk_value()：从模型获取主键值
    - create_model()：从表单创建新模型
    - update_model()：从表单更新现有模型
    - delete_model()：删除模型
    - _create_ajax_loader()：创建 AJAX 加载器（如果使用 form_ajax_refs）

    Example:
        ```python
        from flask_exts.admin.model import ModelView

        class UserAdmin(ModelView):
            # 配置
            column_list = ['id', 'username', 'email', 'created_at']
            column_sortable_list = ['username', 'created_at']
            form_columns = ['username', 'email', 'password']

            # 实现抽象方法
            def scaffold_list_columns(self):
                return ['id', 'username', 'email', 'created_at']

            def scaffold_sortable_columns(self):
                return {'username': 'username', 'created_at': 'created_at'}

            def scaffold_form(self):
                # 使用 flask_sqlalchemy 或其他 ORM
                return generate_form_from_model(User)

            def get_list(self, page, sort_field, sort_desc, search, filters, page_size=None):
                query = User.query
                # 应用搜索、排序、过滤和分页
                return count, items
        ```

    Features:
        - 列管理（列表、详情、导出视图）
        - 排序支持
        - 分页支持
        - 值格式化和类型转换
        - 表单生成和处理
        - CRUD 操作
        - 导出功能（CSV、JSON、Excel 等）
        - 操作和行操作
        - 过滤和搜索
    """

    pass
