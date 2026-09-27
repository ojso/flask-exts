"""
Form management / 表单管理

English summary: This module manages admin model-view forms, including scaffolding, generation, instantiation, and URL handling.
中文说明：负责管理 Admin 模型视图中的表单，包括表单脚手架、表单生成、表单实例化和返回 URL 处理。
"""

from typing import Optional, Type, Any, Dict, Callable
from wtforms.fields import HiddenField
from wtforms.validators import InputRequired
from wtforms.fields.core import UnboundField
from ....forms.form.flask_form import FlaskForm
from ....forms.widgets import EditableWidget


class FormsMixin:
    """
    Form management mixin / 表单管理功能混入类

    English summary: Provides form scaffolding, creation, retrieval, and handling utilities for model views.
    中文说明：提供表单脚手架、创建、获取和处理功能。
    """

    base_form_class = FlaskForm
    """English: comment / 表单基类"""

    # English: ModelView / 表单配置属性（继承自 ModelView）
    form_args: Dict[str, Dict[str, Any]] = {}
    """English: comment / 表单字段参数"""

    form_columns: Optional[list] = None
    """English: comment / 表单字段列表"""

    form_excluded_columns: Optional[list] = None
    """English: comment / 排除的表单字段"""

    form_widget_args: Optional[Dict[str, Dict[str, Any]]] = None
    """English: comment / 表单小部件参数"""

    form_extra_fields: Optional[Dict[str, Any]] = None
    """English: comment / 额外的表单字段"""

    form_ajax_refs: Optional[Dict[str, Any]] = None
    """English: AJAX / AJAX 参考配置"""

    # English: comment / 缓存的表单类
    _create_form_class: Optional[Type] = None
    _edit_form_class: Optional[Type] = None
    _delete_form_class: Optional[Type] = None
    _list_form_class: Optional[Type] = None
    _form_ajax_refs: Dict[str, Any] = {}

    def scaffold_form(self) -> Type:
        """
        Create `form.BaseForm` inherited class from the model. Must be implemented in the child class.

        English summary: Build a form class from the model; child classes must implement this method.
        中文说明：从模型创建表单类，必须在子类中实现。

        Returns:
            Type: Form class / 表单类

        Raises:
            NotImplementedError: must be implemented in subclass / 必须在子类中实现
        """
        return None

    def scaffold_list_form(self, widget=None, validators=None) -> type:
        """
        Create form for the `index_view` using only the columns from
        `self.column_editable_list`.

        :param widget:
            WTForms widget class. Defaults to `EditableWidget`.
        :param validators:
            `form_args` dict with only validators
            {'name': {'validators': [DataRequired()]}}

        Must be implemented in the child class.

        English summary: Build a form for the list view, using only editable columns defined for the index view.
        中文说明：为 index_view（列表视图）创建表单，仅使用 column_editable_list 中的列。

        Args:
            widget (Optional[Any]): WTForms widget class, default is EditableWidget / WTForms 小部件类，默认为 EditableWidget
            validators (Optional[Dict]): Form argument dict containing only validators / 表单参数字典，仅包含验证器，例如 {'name': {'validators': [DataRequired()]}}

        Returns:
            Type: Form class / 表单类

        Raises:
            NotImplementedError: must be implemented in subclass / 必须在子类中实现
        """
        raise NotImplementedError("Please implement scaffold_list_form method")

    def get_list_form(self) -> type:
        """
        Get form class for the editable list view.

        Uses only validators from `form_args` to build the form class.

        Allows overriding the editable list view field/widget. For example::

            from .model.widgets import EditableWidget

            class CustomWidget(EditableWidget):
                def get_kwargs(self, subfield, kwargs):
                    if subfield.type == 'TextAreaField':
                        kwargs['data-type'] = 'textarea'
                        kwargs['data-rows'] = '20'
                    # elif: kwargs for other fields

                    return kwargs

            class MyModelView(BaseModelView):
                def get_list_form(self):
                    return self.scaffold_list_form(widget=CustomWidget)

        English summary: Return the editable list form, using only validators from form_args and allowing widget overrides.
        中文说明：获取可编辑列表视图的表单类。仅使用 form_args 中的验证器来构建表单类，并允许重写可编辑列表视图的字段/小部件。

        Returns:
            Type: Form class
        """
        if self.form_args:
            # English: form_args FieldList / 仅获取验证器，其他 form_args 可能会破坏 FieldList 包装
            validators = {
                key: {"validators": value["validators"]}
                for key, value in self.form_args.items()
                if value.get("validators")
            }
        else:
            validators = None

        return self.scaffold_list_form(validators=validators)

    def create_editable_list_form(self, form_class, widget=None):
        """
        Create a form class with all the fields wrapped in a FieldList.

        Wrapping each field in FieldList allows submitting POST requests
        in this format: ('<field_name>-<primary_key>', '<value>')

        Used in the editable list view.

        :param base_form_class:
            WTForms form class, by default `base_form_class` from base.
        :param form_class:
            WTForms form class generated by `form.get_form`.
        :param widget:
            WTForms widget class. Defaults to `EditableWidget`.
        """
        if widget is None:
            widget = EditableWidget()

        class ListForm(self.base_form_class):
            pk = HiddenField(validators=[InputRequired()])

        for name, obj in form_class.__dict__.items():
            if not name.startswith("_") and isinstance(obj, UnboundField):
                if name == "pk":
                    raise Exception("Form already has a pk column.")
                obj.kwargs["widget"] = widget
                setattr(ListForm, name, obj)

        return ListForm

    def get_create_form(self) -> Type:
        """
        Create form class for model creation view.

        Override to implement customized behavior.

        English summary: Return the form used for the create view; override this method to customize behavior.
        中文说明：创建模型创建视图的表单类，覆盖以实现自定义行为。

        Returns:
            Type: Form class / 表单类
        """
        return self.scaffold_form()

    def get_edit_form(self) -> Type:
        """
        Create form class for model editing view.

        Override to implement customized behavior.

        English summary: Return the form used for the edit view; override this method to customize behavior.
        中文说明：创建模型编辑视图的表单类，覆盖以实现自定义行为。

        Returns:
            Type: Form class / 表单类
        """
        return self.scaffold_form()

    def get_delete_form(self) -> Type:
        """
        Create form class for model delete view.

        Override to implement customized behavior.

        English summary: Return the delete form; override this method to customize behavior.
        中文说明：创建模型删除视图的表单类，覆盖以实现自定义行为。

        Returns:
            Type: Form class / 表单类
        """

        class DeleteForm(self.base_form_class):
            id = HiddenField(validators=[InputRequired()])

        return DeleteForm

    def create_form(self, *args, **kwargs) -> Any:
        """
        Instantiate model creation form and return it.

        Override to implement custom behavior.

        English summary: Instantiate and return the create form; override to customize behavior.
        中文说明：实例化模型创建表单并返回，覆盖以实现自定义行为。

        Returns:
            Any: Form instance / 表单实例
        """
        return self._create_form_class(*args, **kwargs)

    def edit_form(self, *args, **kwargs) -> Any:
        """
        Instantiate model editing form and return it.

        Override to implement custom behavior.

        English summary: Instantiate and return the edit form; override to customize behavior.
        中文说明：实例化模型编辑表单并返回，覆盖以实现自定义行为。

        Returns:
            Any: Form instance / 表单实例
        """
        return self._edit_form_class(*args, **kwargs)

    def delete_form(self, *args, **kwargs) -> Any:
        """
        Instantiate model delete form and return it.

        Override to implement custom behavior.

        English summary: Instantiate and return the delete form; override to customize behavior.
        中文说明：实例化模型删除表单并返回，覆盖以实现自定义行为。

        Returns:
            Any: Form instance / 表单实例
        """
        return self._delete_form_class(*args, **kwargs)

    def list_form(self, *args, **kwargs) -> Any:
        """
        Instantiate and return the list-edit form for the index view; override to customize behavior.

        Returns:
            Any: Form instance / 表单实例
        """
        return self._list_form_class(*args, **kwargs)

    def get_save_return_url(self, model: Any, is_created: bool = False) -> str:
        """
        Return url where user is redirected after successful form save.

        :param model:
            Saved object
        :param is_created:
            Whether new object was created or existing one was updated

        For example, redirect use to object details view after form save::

            class MyModelView(ModelView):
                def get_save_return_url(self, model, is_created):
                    return self.get_url('.details_view', id=model.id)

        返回成功保存表单后用户被重定向到的 URL。

        Args:
            model (Any): 保存的对象
            is_created (bool): 是否创建了新对象（True）或更新了现有对象（False）

        Returns:
            str: 重定向 URL

        Example:
            重定向到对象详情视图：

            ```python
            class MyModelView(ModelView):
                def get_save_return_url(self, model, is_created):
                    return self.get_url('.details_view', id=model.id)
            ```
        """
        return (
            self.get_url(".details_view", id=model.id)
            if hasattr(self, "get_url")
            else "#"
        )
