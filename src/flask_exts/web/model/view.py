"""
ModelView - admin model view core / ModelView - 管理模型视图主类

English summary: This module provides the streamlined ModelView class, which inherits BaseModelView to gain the full admin feature set.
中文说明：这个模块提供了简化后的 ModelView 类，通过继承 BaseModelView 来获得所有功能。BaseModelView 组合了所有核心功能模块和操作模块。

Improvements:
- Separation of responsibilities: core features moved into dedicated modules / 职责分离：核心功能分离到独立模块
- Easier to test and maintain / 更易于测试和维护
- 100% backward compatibility retained / 保持 100% 向后兼容性

Architecture:
    ModelView (this file, < 300 lines)
    ├── view routes such as index_view, create_view, etc. / 视图路由方法（index_view, create_view 等）
    └── inherits BaseModelView / 继承自 BaseModelView
        ├── View (Flask base view) / View（基础 Flask 视图）
        ├── ColumnsMixin (column management) / ColumnsMixin（列管理）
        ├── SortingMixin (sorting management) / SortingMixin（排序管理）
        ├── PaginationMixin (pagination management) / PaginationMixin（分页管理）
        ├── ValuesMixin (value handling) / ValuesMixin（值处理）
        ├── FormsMixin (form management) / FormsMixin（表单管理）
        ├── ReadOperationsMixin (read operations) / ReadOperationsMixin（读取操作）
        ├── CreateOperationsMixin (create operations) / CreateOperationsMixin（创建操作）
        ├── UpdateOperationsMixin (update operations) / UpdateOperationsMixin（更新操作）
        ├── DeleteOperationsMixin (delete operations) / DeleteOperationsMixin（删除操作）
        ├── ExportOperationsMixin (export operations) / ExportOperationsMixin（导出操作）
        ├── ActionsMixin (actions management) / ActionsMixin（动作管理）
        ├── RowActionMixin (row actions) / RowActionMixin（行动作）
        ├── FilterMixin (filter management) / FilterMixin（过滤管理）
        └── FormMixin (form mixin) / FormMixin（表单混入）
"""

from typing import Optional
from math import ceil
from flask import request, redirect, flash, abort, Response, jsonify, get_flashed_messages
from flask_babel import gettext, ngettext
from werkzeug.utils import secure_filename

from ..exposer import expose_url
from .base import BaseModelView
from .type_formatters import BASE_FORMATTERS, EXPORT_FORMATTERS, DETAIL_FORMATTERS


class ModelView(BaseModelView):
    """
    Model view / 模型视图

    English summary: This view does not make assumptions about the backing store, but expects a standard model API with listing, retrieval, creation, update, deletion, and form scaffolding.
    中文说明：此视图不假设底层数据存储方式，但要求遵循标准模型接口，支持列表、查询、创建、更新、删除和表单脚手架。

    This view does not make any assumptions on how models are stored or managed, but expects the following:

        1. The provided model is an object
        2. The model contains properties
        3. Each model contains an attribute which uniquely identifies it (i.e. a primary key for a database model)
        4. It is possible to retrieve a list of sorted models with pagination applied from a data source
        5. You can get one model by its identifier from the data source

    Essentially, if you want to support a new data store, all you have to do is:

        1. Derive from the `ModelView` class
        2. Implement various data-related methods (`get_list`, `get_one`, `create_model`, etc)
        3. Implement automatic form generation from the model representation (`scaffold_form`)

    Provides complete admin interface functionality, including list, create, edit, delete, detail, and export features / 提供完整的 Admin 界面功能，包括列表、创建、编辑、删除、详情和导出。

    This class is a direct extension of BaseModelView, which composes all functional modules / 这个类是 BaseModelView 的直接扩展，后者组合了所有功能模块。
    ModelView mainly defines route methods and initialization logic / ModelView 只定义了路由视图方法和初始化逻辑。

    Attributes:
        base_form_class: base form class / 表单基类
        can_create: whether creation is allowed / 是否允许创建
        can_edit: whether editing is allowed / 是否允许编辑
        can_delete: whether deletion is allowed / 是否允许删除

    Example:
        ```python
        from flask_exts.admin.model import ModelView

        class UserAdmin(ModelView):
            column_list = ['id', 'username', 'email', 'created_at']
            column_sortable_list = ['username', 'created_at']

            def scaffold_list_columns(self):
                return ['id', 'username', 'email', 'created_at']
        ```
    """

    def __init__(
        self,
        model,
        name=None,
        endpoint=None,
        url=None,
        static_folder=None,
    ):
        """
        Constructor.

        :param model:
            Model class
        :param name:
            View name. If not provided, will use the model class name
        :param endpoint:
            Base endpoint. If not provided, will use the model name.
        :param url:
            Base URL. If not provided, will use endpoint as a URL.
        :param static_folder:
            Static folder for the view. If not provided, will use the default static folder.
        """
        self.model = model

        if name is None:
            name = self._prettify_class_name(model.__name__)

        if endpoint is None:
            endpoint = self.model.__name__.lower()

        super().__init__(
            name,
            endpoint,
            url,
            static_folder,
        )

        self._init_view()

    def _init_view(self):
        """English: comment / 初始化视图配置"""
        self._list_columns = self.get_list_columns()
        self._sortable_columns = self.get_sortable_columns()
        self._details_columns = self.get_details_columns()
        self._export_columns = self.get_export_columns()

        # English: initialize Mixin / 初始化 Mixin
        if hasattr(self, 'init_actions'):
            self.init_actions()
        if hasattr(self, 'init_row_actions'):
            self.init_row_actions()
        if hasattr(self, 'init_filters'):
            self.init_filters()

        self._init_forms()

        # English: comment / 设置默认的格式化器
        if self.column_formatters_export is None:
            self.column_formatters_export = self.column_formatters

        if self.column_formatters_detail is None:
            self.column_formatters_detail = self.column_formatters

        # English: comment / 导入类型格式化器的默认值
        

        if self.column_type_formatters is None:
            self.column_type_formatters = dict(BASE_FORMATTERS)

        if self.column_type_formatters_export is None:
            self.column_type_formatters_export = dict(EXPORT_FORMATTERS)

        if self.column_type_formatters_detail is None:
            self.column_type_formatters_detail = dict(DETAIL_FORMATTERS)

        if self.column_descriptions is None:
            self.column_descriptions = dict()

    def _init_forms(self):
        """English: comment / 初始化表单"""
        self._form_ajax_refs = self._process_ajax_references()

        if self.form_widget_args is None:
            self.form_widget_args = {}

        self._create_form_class = self.get_create_form()
        self._edit_form_class = self.get_edit_form()
        self._delete_form_class = self.get_delete_form()

        # English: comment / 列表视图内联编辑
        if self.column_editable_list:
            self._list_form_class = self.get_list_form()
        else:
            self.column_editable_list = {}

    def is_editable(self, name: str) -> bool:
        """
        Verify if column is editable.

        :param name:
            Column name.

        验证列是否可编辑。

        Args:
            name (str): 列名

        Returns:
            bool: 如果列可编辑返回 True
        """
        return name in self.column_editable_list and self.can_edit

    def is_action_allowed(self, name: str) -> bool:
        """English: comment / 验证操作是否被允许"""
        if name == "delete" and not self.can_delete:
            return False
        return super().is_action_allowed(name) if hasattr(super(), 'is_action_allowed') else True

    def _process_ajax_references(self):
        """
        处理 AJAX 参考配置
        Process `form_ajax_refs` and generate model loaders that will be used by the `ajax_lookup` view.
        """
        result = {}

        if self.form_ajax_refs:
            from .ajax import AjaxModelLoader

            for name, options in self.form_ajax_refs.items():
                if isinstance(options, AjaxModelLoader):
                    result[name] = options
                else:
                    result[name] = self._create_ajax_loader(name, options)
        return result

    def _create_ajax_loader(self, name, options):
        """English: create AJAX Model backend will override / 创建 AJAX 加载器 Model backend will override this to implement AJAX model loading."""
        raise NotImplementedError()

    def get_redirect_target(self, param_name="url", endpoint=".index_view"):
        """English: URL / 获取重定向目标 URL"""
        return request.values.get(param_name) or self.get_url(endpoint)

    # English: comment / =========== 视图路由方法 ===========

    @expose_url("/")
    def index_view(self):
        """Index view"""

        # Grab parameters from URL
        view_args = self._get_list_args()

        # English: comment / 根据列索引映射列名
        # Map column index to column name
        sort_column = self._get_column_by_idx(view_args.sort)
        if sort_column is not None:
            sort_column = sort_column[0]

        # English: comment / 获取安全的页大小
        # Get page size
        page_size = self.get_safe_page_size(view_args.page_size)

        # English: comment / 获取数据
        # Get count and data
        count, data = self.get_list(
            view_args.page,
            sort_column,
            view_args.sort_desc,
            view_args.search,
            view_args.filters,
            page_size=page_size,
        )

        # English: comment / 计算页数
        # Calculate number of pages
        if count is not None and page_size:
            num_pages = int(ceil(count / float(page_size)))
        elif not page_size:
            num_pages = 0  # 隐藏分页器 hide pager for unlimited page_size
        else:
            num_pages = None  # 使用简单分页器 use simple pager

        # English: URL / URL 生成辅助函数
        # Various URL generation helpers
        def pager_url(p):
            # Do not add page number if it is first page
            if p == 0:
                p = None
            return self._get_list_url(view_args.clone(page=p))

        def sort_url(column, invert=False, desc=None):
            if not desc and invert and not view_args.sort_desc:
                desc = 1
            return self._get_list_url(view_args.clone(sort=column, sort_desc=desc))

        def page_size_url(s):
            return self._get_list_url(view_args.clone(page_size=s))

        clear_search_url = self._get_list_url(
            view_args.clone(
                page=0,
                sort=view_args.sort,
                sort_desc=view_args.sort_desc,
                search=None,
                filters=None,
            )
        )

        return self.render(
            self.list_template,
            data=data,
            # list
            list_columns=self._list_columns,
            sortable_columns=self._sortable_columns,
            editable_columns=self.column_editable_list,
            # Pagination
            count=count,
            pager_url=pager_url,
            num_pages=num_pages,
            page_size_url=page_size_url,
            page=view_args.page,
            page_size=page_size,
            default_page_size=self.page_size,
            # sort
            sort_column=view_args.sort,
            sort_desc=view_args.sort_desc,
            sort_url=sort_url,
            # search
            clear_search_url=clear_search_url,
            search=view_args.search,
            # filter
            active_filters=view_args.filters,
            filter_args=self.get_active_filters_kwargs(view_args.filters) if hasattr(self, 'get_active_filters_kwargs') else {},
            # misc
            return_url=self._get_list_url(view_args),
            extra_args=view_args.extra_args,
        )

    @expose_url("/new/", methods=("GET", "POST"))
    def create_view(self):
        """Create model view"""
        return_url = self.get_redirect_target()

        if not self.can_create:
            return redirect(return_url)

        form = self.create_form()

        if form.validate_on_submit():
            model = self.create_model(form)
            if model:
                flash(gettext("Record was successfully created."), "success")
                if "_add_another" in request.form:
                    return redirect(request.url)
                elif "_continue_editing" in request.form:
                    if model is not True:
                        url = self.get_url(
                            ".edit_view", id=self.get_pk_value(model), url=return_url
                        )
                    else:
                        url = return_url
                    return redirect(url)
                else:
                    return redirect(self.get_save_return_url(model, is_created=True))

        form_opts = dict(widget_args=self.form_widget_args)

        if self.create_modal and request.args.get("modal"):
            template = self.create_modal_template
        else:
            template = self.create_template

        return self.render(
            template, form=form, form_opts=form_opts, return_url=return_url
        )

    @expose_url("/edit/", methods=("GET", "POST"))
    def edit_view(self):
        """Edit model view"""
        return_url = self.get_redirect_target()

        if not self.can_edit:
            return redirect(return_url)

        id = request.args.get("id")

        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext("Record does not exist."), "error")
            return redirect(return_url)

        form = self._edit_form_class(obj=model)

        if form.validate_on_submit():
            if self.update_model(form, model):
                flash(gettext("Record was successfully saved."), "success")
                if "_add_another" in request.form:
                    return redirect(self.get_url(".create_view", url=return_url))
                elif "_continue_editing" in request.form:
                    return redirect(
                        self.get_url(".edit_view", id=self.get_pk_value(model))
                    )
                else:
                    return redirect(self.get_save_return_url(model, is_created=False))

        form_opts = dict(widget_args=self.form_widget_args)

        if self.edit_modal and request.args.get("modal"):
            template = self.edit_modal_template
        else:
            template = self.edit_template

        return self.render(
            template, model=model, form=form, form_opts=form_opts, return_url=return_url
        )

    @expose_url("/details/")
    def details_view(self):
        """Details model view"""
        return_url = self.get_redirect_target()

        id = request.args.get("id")

        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext("Record does not exist."), "error")
            return redirect(return_url)

        if self.details_modal and request.args.get("modal"):
            template = self.details_modal_template
        else:
            template = self.details_template

        return self.render(
            template,
            model=model,
            details_columns=self._details_columns,
            return_url=return_url,
        )

    @expose_url("/delete/", methods=("POST",))
    def delete_view(self):
        """Delete model view. Only POST method is allowed."""
        return_url = self.get_redirect_target()
        if not self.can_delete:
            return redirect(return_url)

        form = self.delete_form()
        if form.validate():
            id = form.id.data
            model = self.get_one(id)
            if model is None:
                flash(gettext("Record does not exist."), "error")
                return redirect(return_url)

            if self.delete_model(model):
                count = 1
                flash(
                    ngettext(
                        "Record was successfully deleted.",
                        "%(count)s records were successfully deleted.",
                        count,
                        count=count,
                    ),
                    "success",
                )
                return redirect(return_url)
        else:
            if hasattr(form, 'flash_errors'):
                form.flash_errors(message="Failed to delete record. %(error)s")

        return redirect(return_url)

    @expose_url("/ajax/lookup/")
    def ajax_lookup(self):
        """AJAX lookup"""
        name = request.args.get("name")
        query = request.args.get("query")
        offset = request.args.get("offset", type=int)
        limit = request.args.get("limit", 10, type=int)
        loader = self._form_ajax_refs.get(name)
        if not loader:
            abort(404)

        data = [loader.format(m) for m in loader.get_list(query, offset, limit)]
        return jsonify(data)

    @expose_url("/ajax/update/", methods=("POST",))
    def ajax_update(self):
        """Ajax update. Edits a single column of a record in list view."""
        if not self.column_editable_list:
            abort(404)

        form = self.list_form()
        for field in list(form):
            print(field)
            print(field.name,field._value)

        # English: comment / 防止验证问题 - 删除未提交的字段
        for field in list(form):
            if (field.name in request.form) or (field.name == "csrf_token"):
                pass
            else:
                form.__delitem__(field.name)

        if form.validate_on_submit():
            pk = form.list_form_pk.data
            record = self.get_one(pk)

            if record is None:
                return gettext("Record does not exist."), 500

            if self.update_model(form, record):
                return gettext("Record was successfully saved.")
            else:
                msgs = ", ".join([msg for msg in get_flashed_messages()])
                return gettext("Failed to update record. %(error)s", error=msgs), 500
        else:
            for field in form:
                for error in field.errors:
                    if isinstance(error, list):
                        return (
                            gettext(
                                "Failed to update record. %(error)s",
                                error=", ".join(error),
                            ),
                            500,
                        )
                    else:
                        return (
                            gettext("Failed to update record. %(error)s", error=error),
                            500,
                        )

        return gettext("Validation failed."), 400
