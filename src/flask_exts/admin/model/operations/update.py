from typing import Any


class UpdateOperationsMixin:
    def update_model(self, form: Any, model: Any) -> bool:
        """
        Update model from the form.

        Must be implemented in the child class.

        Args:
            form:
                Form instance
            model:
                Model instance

        Returns:
            bool: Returns `True` if operation succeeded, else `False`

        Raises:
            NotImplementedError

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
