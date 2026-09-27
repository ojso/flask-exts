"""Create-operation mixin for model-backed admin views."""

from typing import Any, Union


class CreateOperationsMixin:
    """Mixin that defines the create-model hook used by admin views."""

    def create_model(self, form: Any) -> Union[Any, bool]:
        """Create a model instance from form data.

        This method must be implemented by the subclass.

        Args:
            form: WTForms form instance.

        Returns:
            Union[Any, bool]: The created model instance, or ``True`` when the
                method succeeds without returning an instance.

        Raises:
            NotImplementedError: If the subclass does not implement the hook.

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
