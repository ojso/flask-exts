"""
更新操作 (Update Operations)

负责更新现有模型的操作。
"""

from typing import Any, Optional


class UpdateOperationsMixin:
    """
    更新操作功能混入类。

    提供 update_model 方法。
    """

    def update_model(self, form: Any, model: Any) -> bool:
        """
        从表单更新模型。

        如果操作成功则返回 True。

        必须在子类中实现。

        Args:
            form (Any): 表单实例
            model (Any): 要更新的模型实例

        Returns:
            bool: 如果操作成功返回 True，否则返回 False

        Raises:
            NotImplementedError: 必须在子类中实现

        Example:
            ```python
            def update_model(self, form, model):
                form.populate_obj(model)
                db.session.add(model)
                db.session.commit()
                return True
            ```
        """
        raise NotImplementedError("Please implement update_model method")
