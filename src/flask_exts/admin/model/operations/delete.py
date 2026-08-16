"""
删除操作 (Delete Operations)

负责删除模型的操作。
"""

from typing import Any


class DeleteOperationsMixin:
    """
    删除操作功能混入类。

    提供 delete_model 方法。
    """

    def delete_model(self, model: Any) -> bool:
        """
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
