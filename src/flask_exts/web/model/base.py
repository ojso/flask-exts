from typing import Optional
from .types import T_COLUMN_LIST, T_FORMATTERS
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
from .row_actions import RowActionMixin
from .filter_mixin import FilterMixin


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
):
    """

    English summary: This base class is abstract. Concrete backend implementations should inherit it and implement the required abstract methods below.
    中文说明：这个类是抽象的。特定的后端实现应该继承这个类，并实现下面的抽象方法。

    - scaffold_list_columns(): return the column list from the model / 从模型获取列列表
    - scaffold_sortable_columns(): return the sortable column list / 从模型获取可排序列列表
    - scaffold_form(): build a form class from the model / 从模型生成表单类
    - scaffold_list_form(): build a list-edit form from the model / 从模型生成列表编辑表单
    - get_list(): fetch paginated data from the model / 获取分页数据列表
    - get_one(): fetch one model by id / 按 ID 获取单个模型
    - get_pk_value(): read the primary key value from a model / 从模型获取主键值
    - create_model(): create a new model from a form / 从表单创建新模型
    - update_model(): update an existing model from a form / 从表单更新现有模型
    - delete_model(): delete a model / 删除模型
    - _create_ajax_loader(): create an AJAX loader when form_ajax_refs is used / 创建 AJAX 加载器（如果使用 form_ajax_refs）

    Example:
        ```python
        from flask_exts.admin.model import ModelView

        class UserAdmin(ModelView):
            # English: configuration / 配置
            column_list = ['id', 'username', 'email', 'created_at']
            column_sortable_list = ['username', 'created_at']
            form_columns = ['username', 'email', 'password']

            # English: comment / 实现抽象方法
            def scaffold_list_columns(self):
                return ['id', 'username', 'email', 'created_at']

            def scaffold_sortable_columns(self):
                return {'username': 'username', 'created_at': 'created_at'}

            def scaffold_form(self):
                # English: use flask_sqlalchemy ORM / 使用 flask_sqlalchemy 或其他 ORM
                return generate_form_from_model(User)

            def get_list(self, page, sort_field, sort_desc, search, filters, page_size=None):
                query = User.query
                # English: apply search, sorting, filtering and pagination / 应用搜索、排序、过滤和分页
                return count, items
        ```

    Features:
        - Column management for list, detail, and export views / 列管理（列表、详情、导出视图）
        - Sorting support / 排序支持
        - Pagination support / 分页支持
        - Value formatting and type conversion / 值格式化和类型转换
        - Form generation and handling / 表单生成和处理
        - CRUD operations / CRUD 操作
        - Export support (CSV, JSON, Excel, etc.) / 导出功能（CSV、JSON、Excel 等）
        - Actions and row actions / 操作和行操作
        - Filtering and searching / 过滤和搜索
    """

    # Permissions
    can_create = True
    """Is model creation allowed"""

    can_edit = True
    """Is model editing allowed"""

    can_delete = True
    """Is model deletion allowed"""

    # Templates
    list_template = "admin/model/list.html"
    """Default list view template"""

    edit_template = "admin/model/edit.html"
    """Default edit template"""

    create_template = "admin/model/create.html"
    """Default create template"""

    details_template = "admin/model/details.html"
    """Default details view template"""

    # Modal Templates
    edit_modal_template = "admin/model/modals/edit.html"
    """Default edit modal template"""

    create_modal_template = "admin/model/modals/create.html"
    """Default create modal template"""

    details_modal_template = "admin/model/modals/details.html"
    """Default details modal view template"""

    # Modals
    edit_modal = False
    """Setting this to true will display the edit_view as a modal dialog."""

    create_modal = False
    """Setting this to true will display the create_view as a modal dialog."""

    details_modal = False
    """Setting this to true will display the details_view as a modal dialog."""

    

    column_formatters = dict()
    """
        Dictionary of list view column formatters.

        For example, if you want to show price multiplied by
        two, you can do something like this::

            class MyModelView(BaseModelView):
                column_formatters = dict(price=lambda v, m, p: m.price*2)

        The Callback function has the prototype::

            def formatter(view, model, name):
                # `view` is current administrative view
                # `model` is model instance
                # `name` is property name
                pass
    """

    column_formatters_export = None
    """
        Dictionary of list view column formatters to be used for export.
        Defaults to column_formatters when set to None.
    """

    column_formatters_detail = None
    """
        Dictionary of list view column formatters to be used for the detail view.
        Defaults to column_formatters when set to None.
    """

    column_type_formatters: Optional[T_FORMATTERS] = None
    """
        Dictionary of value type formatters to be used in the list view.

        By default, three types are formatted:

        1. ``None`` will be displayed as an empty string
        2. ``bool`` will be displayed as a checkmark if it is ``True``
        3. ``list`` will be joined using ', '

        If you don't like the default behavior and don't want any type formatters
        applied, just override this property with an empty dictionary::

            class MyModelView(BaseModelView):
                column_type_formatters = dict()

        If you want to display `NULL` instead of an empty string, you can do
        something like this. Also comes with bonus `date` formatter::

            from datetime import date
            from .model import typefmt

            def date_format(view, value):
                return value.strftime('%d.%m.%Y')

            MY_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
            MY_DEFAULT_FORMATTERS.update({
                    type(None): typefmt.null_formatter,
                    date: date_format
                })

            class MyModelView(BaseModelView):
                column_type_formatters = MY_DEFAULT_FORMATTERS

        Type formatters have lower priority than list column formatters.

        The callback function has following prototype::

            def type_formatter(view, value):
                # `view` is current administrative view
                # `value` value to format
                pass
    """

    column_type_formatters_export = None
    """
        Dictionary of value type formatters to be used in the export.

        By default, two types are formatted:

        1. ``None`` will be displayed as an empty string
        2. ``list`` will be joined using ', '

        Functions the same way as column_type_formatters.
    """

    column_type_formatters_detail = None
    """
        Dictionary of value type formatters to be used in the detail view.

        By default, two types are formatted:

        1. ``None`` will be displayed as an empty string
        2. ``list`` will be joined using ', '

        Functions the same way as column_type_formatters.
    """

    column_labels = {}
    """
        Dictionary where key is column name and value is string to display.

        For example::

            class MyModelView(BaseModelView):
                column_labels = dict(name='Name', last_name='Last Name')
    """

    column_descriptions = None
    """
        Dictionary where key is column name and
        value is description for `list view` column or add/edit form field.

        For example::

            class MyModelView(BaseModelView):
                column_descriptions = dict(
                    full_name='First and Last name'
                )
    """

    column_sortable_list: Optional[T_COLUMN_LIST] = None
    """
        Collection of the sortable columns for the list view.
        If set to `None`, will get them from the model.

        For example::

            class MyModelView(BaseModelView):
                column_sortable_list = ('name', 'last_name')

        If you want to explicitly specify field/column to be used while
        sorting, you can use a tuple::

            class MyModelView(BaseModelView):
                column_sortable_list = ('name', ('user', 'user.username'))

        You can also specify multiple fields to be used while sorting::

            class MyModelView(BaseModelView):
                column_sortable_list = (
                    'name', ('user', ('user.first_name', 'user.last_name')))
        When using SQLAlchemy models, model attributes can be used instead
        of strings::

            class MyModelView(BaseModelView):
                column_sortable_list = ('name', ('user', 'user.username'))
    """

    column_default_sort = None
    """
        Default sort column if no sorting is applied.

        Example::

            class MyModelView(BaseModelView):
                column_default_sort = 'user'

        You can use tuple to control ascending descending order. In following example, items
        will be sorted in descending order::

            class MyModelView(BaseModelView):
                column_default_sort = ('user', True)

        If you want to sort by more than one column,
        you can pass a list of tuples::

            class MyModelView(BaseModelView):
                column_default_sort = [('name', True), ('last_name', True)]
    """

    column_searchable_list: Optional[T_COLUMN_LIST] = None
    """
        A collection of the searchable columns. It is assumed that only
        text-only fields are searchable, but it is up to the model
        implementation to decide.

        Example::

            class MyModelView(ModelView):
                column_searchable_list = ('name', 'email')

        You can also pass relation.column::

            class MyModelView(ModelView):
                column_searchable_list = (user.name, user.email)

    """

    column_editable_list = None
    """
        Collection of the columns which can be edited from the list view.

        For example::

            class MyModelView(BaseModelView):
                column_editable_list = ('name', 'last_name')
    """

    column_choices = {}
    """
        Map choices to columns in list view

        Example::

            class MyModelView(BaseModelView):
                column_choices = {
                    'my_column': {
                        'db_value': 'display_value',
                        'db_value2': 'display_value2',
                    }
                }
    """

    form_args = {}
    """
        Dictionary of form field arguments. Refer to WTForms documentation for
        list of possible options.

        Example::

            from wtforms.validators import DataRequired
            class MyModelView(BaseModelView):
                form_args = dict(
                    name=dict(label='First Name', validators=[DataRequired()])
                )
    """

    form_columns = None
    """
        Collection of the model field names for the form. If set to `None` will
        get them from the model.

        Example::

            class MyModelView(BaseModelView):
                form_columns = ('name', 'email')

        SQLAlchemy model attributes can be used instead of strings::

            class MyModelView(BaseModelView):
                form_columns = ('name', 'user.last_name')
    """

    form_excluded_columns = None
    """
        Collection of excluded form field names.

        For example::

            class MyModelView(BaseModelView):
                form_excluded_columns = ('last_name', 'email')
    """

    form_widget_args = None
    """
        Dictionary of form widget rendering arguments.
        Use this to customize how widget is rendered without using custom template.

        Example::

            class MyModelView(BaseModelView):
                form_widget_args = {
                    'description': {
                        'rows': 10,
                        'style': 'color: black'
                    },
                    'other_field': {
                        'disabled': True
                    }
                }

        Changing the format of a DateTimeField will require changes to both form_widget_args and form_args.

        Example::

            form_args = dict(
                start=dict(format='%Y-%m-%d %I:%M %p') # changes how the input is parsed by strptime (12 hour time)
            )
            form_widget_args = dict(
                start={
                    'data-date-format': u'yyyy-mm-dd HH:ii P',
                    'data-show-meridian': 'True'
                } # changes how the DateTimeField displays the time
            )
    """

    form_extra_fields = None
    """
        Dictionary of additional fields.

        Example::

            class MyModelView(BaseModelView):
                form_extra_fields = {
                    'password': PasswordField('Password')
                }

        You can control order of form fields using ``form_columns`` property. For example::

            class MyModelView(BaseModelView):
                form_columns = ('name', 'email', 'password', 'secret')

                form_extra_fields = {
                    'password': PasswordField('Password')
                }

        In this case, password field will be put between email and secret fields that are autogenerated.
    """

    form_ajax_refs = None
    """
        Use AJAX for foreign key model loading.

        Should contain dictionary, where key is field name and value is either a dictionary which
        configures AJAX lookups or backend-specific `AjaxModelLoader` class instance.

        For example, it can look like::

            class MyModelView(BaseModelView):
                form_ajax_refs = {
                    'user': {
                        'fields': ('first_name', 'last_name', 'email'),
                        'placeholder': 'Please select',
                        'page_size': 10,
                        'minimum_input_length': 0,
                    }
                }

        Or with SQLAlchemy backend like this::

            class MyModelView(BaseModelView):
                form_ajax_refs = {
                    'user': AjaxSqlaModelLoader('user', User, self.session, fields=['email'], page_size=10)
                }
    """



