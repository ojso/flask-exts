"""
创建操作 (Create Operations)

负责创建新模型的操作。
"""

from typing import Any, Union, Optional


class CreateOperationsMixin:
    """
    创建操作功能混入类。

    提供 create_model 方法。
    """

    def create_model(self, form: Any) -> Union[Any, bool]:
        """
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
