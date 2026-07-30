from .rowaction import ViewRowAction, EditRowAction, DeleteRowAction
from .rowaction import ViewPopupRowAction, EditPopupRowAction


class RowActionMixin:
    def __init__(self, *args, **kwargs):
        self._row_actions = []
        super().__init__(*args, **kwargs)

    def init_row_actions(self):
        """
        Return list of row action objects to display in the list view.
        """

        if self.details_modal:
            self._row_actions.append(ViewPopupRowAction())
        else:
            self._row_actions.append(ViewRowAction())

        if self.can_edit:
            if self.edit_modal:
                self._row_actions.append(EditPopupRowAction())
            else:
                self._row_actions.append(EditRowAction())

        if self.can_delete:
            self._row_actions.append(DeleteRowAction())

    def get_row_actions(self):
        """
        Return a list of row actions.
        Override this method to provide custom row actions.
        """
        return self._row_actions
