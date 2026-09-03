"""
Value processing / 值处理

English summary: This module handles value extraction, formatting, and transformation for Admin model views, including nested attributes and choice mappings.
中文说明：负责管理 Admin 模型视图中的值提取、格式化和处理，包括获取模型属性、应用格式化器和处理选择项等。
"""

from typing import Optional, Dict, Any, Callable
from functools import reduce


class ValuesMixin:
    """
    Value processing mixin / 值处理功能混入类

    English summary: Provides value extraction, formatting, and rendering support for list/detail/export views.
    中文说明：提供值提取、格式化和处理功能。
    """

    # English: ModelView / 值处理配置属性（继承自 ModelView）
    column_formatters: Dict[str, Callable] = {}
    """English: comment / 列表视图的列格式化器"""

    column_formatters_export: Optional[Dict[str, Callable]] = None
    """English: comment / 导出视图的列格式化器"""

    column_formatters_detail: Optional[Dict[str, Callable]] = None
    """English: comment / 详情视图的列格式化器"""

    column_type_formatters: Optional[Dict[type, Callable]] = None
    """English: comment / 类型格式化器（用于列表视图）"""

    column_type_formatters_export: Optional[Dict[type, Callable]] = None
    """English: comment / 类型格式化器（用于导出）"""

    column_type_formatters_detail: Optional[Dict[type, Callable]] = None
    """English: comment / 类型格式化器（用于详情视图）"""

    column_choices: Dict[str, Dict[Any, str]] = {}
    """English: comment / 列选择项映射"""

    def _get_object_attr(self, obj: Any, name: str) -> Any:
        """
        Recursive getattr from the obj by the name. Name can be a dot-delimited string to get nested attributes.

        :param name:
            Dot delimited attribute name, for example 'user.username' to get obj.user.username.
            
        递归从对象中获取属性。

        支持点号分隔的嵌套属性。例如，'user.username' 可以获取 obj.user.username。

        Args:
            obj (Any): 对象
            name (str): 点号分隔的属性名

        Returns:
            Any: 属性值

        Raises:
            AttributeError: 如果属性不存在
        """
        return reduce(getattr, name.split("."), obj)

    def _get_format_value(
        self,
        model: Any,
        name: str,
        column_formatters: Dict[str, Callable],
        column_type_formatters: Optional[Dict[type, Callable]]
    ) -> Any:
        """
        Returns the value to be displayed.

        :param model:
            Model instance
        :param name:
            Field name
        :param column_formatters:
            column_formatters to be used.
        :param column_type_formatters:
            column_type_formatters to be used.

        获取要显示的格式化值。

        应用列格式化器（如果存在），然后应用类型格式化器（如果存在），
        最后应用选择项映射（如果存在）。

        Args:
            model (Any): 模型实例
            name (str): 字段名
            column_formatters (Dict[str, Callable]): 列格式化器
            column_type_formatters (Optional[Dict[type, Callable]]): 类型格式化器

        Returns:
            Any: 格式化后的值
        """
        # English: comment / 首先应用列格式化器
        column_fmt = column_formatters.get(name)
        if column_fmt is not None:
            value = column_fmt(self, model, name)
        else:
            value = self._get_object_attr(model, name)

        # English: comment / 应用选择项映射
        choices_map = self.column_choices.get(name, {})
        if choices_map:
            return choices_map.get(value) or value

        # English: comment / 应用类型格式化器
        if column_type_formatters:
            type_fmt = None
            for typeobj, formatter in column_type_formatters.items():
                if isinstance(value, typeobj):
                    type_fmt = formatter
                    break
            if type_fmt is not None:
                value = type_fmt(self, value, name)

        return value

    def get_list_value(self, model: Any, name: str) -> Any:
        """
        Returns the value to be displayed in the list view

        :param model:
            Model instance
        :param name:
            Field name

        获取列表视图中显示的值。

        使用 column_formatters 和 column_type_formatters。

        Args:
            model (Any): 模型实例
            name (str): 字段名

        Returns:
            Any: 格式化后的值
        """
        column_type_formatters = self.column_type_formatters or {}

        return self._get_format_value(
            model,
            name,
            self.column_formatters,
            column_type_formatters,
        )

    def get_detail_value(self, model: Any, name: str) -> Any:
        """
        Returns the value to be displayed in the detail view

        :param model:
            Model instance
        :param name:
            Field name

        获取详情视图中显示的值。

        使用 column_formatters_detail 和 column_type_formatters_detail。
        如果未设置，则回退到 column_formatters 和 column_type_formatters。

        Args:
            model (Any): 模型实例
            name (str): 字段名

        Returns:
            Any: 格式化后的值
        """
        column_formatters_detail = self.column_formatters_detail or self.column_formatters
        column_type_formatters_detail = self.column_type_formatters_detail or self.column_type_formatters or {}

        return self._get_format_value(
            model,
            name,
            column_formatters_detail,
            column_type_formatters_detail,
        )

    def get_export_value(self, model: Any, name: str) -> Any:
        """
        Returns the value to be displayed in export.
        Allows export to use different (non HTML) formatters.

        :param model:
            Model instance
        :param name:
            Field name

        获取导出视图中显示的值。

        使用 column_formatters_export 和 column_type_formatters_export。
        如果未设置，则回退到 column_formatters 和 column_type_formatters。

        注意：导出值可能使用非 HTML 格式化器。

        Args:
            model (Any): 模型实例
            name (str): 字段名

        Returns:
            Any: 格式化后的值
        """
        column_formatters_export = self.column_formatters_export or self.column_formatters
        column_type_formatters_export = self.column_type_formatters_export or self.column_type_formatters or {}

        return self._get_format_value(
            model,
            name,
            column_formatters_export,
            column_type_formatters_export,
        )

    def get_export_name(self, export_type: str = "csv") -> str:
        """
        获取导出文件名。
        :return: The exported csv file name.
        Returns:
            str: 导出文件名，格式如 'users_2026-08-14_12-30-45.csv'
        """
        import time

        filename = "%s_%s.%s" % (
            self.name,
            time.strftime("%Y-%m-%d_%H-%M-%S"),
            export_type,
        )
        return filename
