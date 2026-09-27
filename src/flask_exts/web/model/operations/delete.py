"""Delete-operation mixin for model-backed admin views."""

from typing import Any


class DeleteOperationsMixin:
    """Mixin that defines the delete-model hook used by admin views."""

    def delete_model(self, model: Any) -> bool:
        """Delete a model instance.

        This method must be implemented by the subclass.

        Args:
            model: Model instance to remove.

        Returns:
            bool: ``True`` if the delete operation succeeded, otherwise ``False``.

        Raises:
            NotImplementedError: If the subclass does not implement the hook.

        Example:
            ```python
            def delete_model(self, model):
                db.session.delete(model)
                db.session.commit()
                return True
            ```
        """
        raise NotImplementedError("Please implement delete_model method")
