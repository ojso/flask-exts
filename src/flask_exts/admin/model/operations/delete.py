"""
Delete operations / 删除操作

English summary: This module defines the mixin for deleting model records.
中文说明：这个模块定义了用于删除模型记录的混入类。
"""

from typing import Any


class DeleteOperationsMixin:
    """
    Delete operations mixin / 删除操作功能混入类

    English summary: Provides the delete_model method for removing model instances.
    中文说明：提供 delete_model 方法，用于删除模型实例。
    """

    def delete_model(self, model: Any) -> bool:
        """
        Delete model.

        Returns `True` if operation succeeded.

        Must be implemented in the child class.

        :param model:
            Model instance

        删除模型。

        如果操作成功则返回 True。

        必须在子类中实现。

        Args:
            model (Any): 要删除的模型实例

        Returns:
            bool: 如果操作成功返回 True，否则返回 False

        Raises:
            NotImplementedError: 必须在子类中实现

        Example:
            ```python
            def delete_model(self, model):
                db.session.delete(model)
                db.session.commit()
                return True
            ```
        """
        raise NotImplementedError("Please implement delete_model method")
