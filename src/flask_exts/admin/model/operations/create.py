"""
Create operations / 创建操作

English summary: This module defines the mixin for creating new model instances from a form.
中文说明：这个模块定义了用于从表单创建新模型实例的混入类。
"""

from typing import Any, Union, Optional


class CreateOperationsMixin:
    """
    Create operations mixin / 创建操作功能混入类

    English summary: Provides the create_model method for instantiating a model from form data.
    中文说明：提供 create_model 方法，用于从表单数据创建模型实例。
    """

    def create_model(self, form: Any) -> Union[Any, bool]:
        """
        Create model from the form.

        Returns the model instance if operation succeeded.

        Must be implemented in the child class.

        :param form:
            Form instance
            
        从表单创建模型。

        如果操作成功则返回模型实例。

        必须在子类中实现。

        Args:
            form (Any): 表单实例

        Returns:
            Union[Any, bool]: 模型实例或 True（表示成功但没有返回模型）

        Raises:
            NotImplementedError: 必须在子类中实现

        Example:
            ```python
            def create_model(self, form):
                model = self.model()
                form.populate_obj(model)
                db.session.add(model)
                db.session.commit()
                return model
            ```
        """
        raise NotImplementedError("Please implement create_model method")
