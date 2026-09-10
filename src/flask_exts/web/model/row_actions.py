from flask import url_for
from flask_babel import lazy_gettext


class BaseRowAction:
    def __init__(self, type=None, title=None, icon=None):
        self.type = type
        self.title = title
        self.icon = icon


class ViewRowAction(BaseRowAction):
    def __init__(self):
        super().__init__(
            type="view_row", title=lazy_gettext("View Record"), icon="view"
        )


class ViewPopupRowAction(BaseRowAction):
    def __init__(self):
        super().__init__(
            type="view_row_popup", title=lazy_gettext("View Record"), icon="view"
        )


class EditRowAction(BaseRowAction):
    def __init__(self):
        super().__init__(
            type="edit_row", title=lazy_gettext("Edit Record"), icon="edit"
        )


class EditPopupRowAction(BaseRowAction):
    def __init__(self):
        super().__init__(
            type="edit_row_popup", title=lazy_gettext("Edit Record"), icon="edit"
        )


class DeleteRowAction(BaseRowAction):
    def __init__(self):
        super().__init__(
            type="delete_row", title=lazy_gettext("Delete Record"), icon="delete"
        )
        self.confirm = lazy_gettext("Are you sure you want to delete this record?")


class LinkRowAction(BaseRowAction):
    def __init__(self, url, title=None, icon=None):
        super().__init__(type="link", title=title, icon=icon)
        self.url = url

    def get_url(self, row_id, row):
        if isinstance(self.url, str):
            url = self.url.format(row_id=row_id)
        else:
            url = self.url(self, row_id, row)
        return url


class EndpointLinkRowAction(BaseRowAction):
    def __init__(self, endpoint, id_arg="id", url_args=None, title=None, icon=None):
        super().__init__(type="link", title=title, icon=icon)
        self.endpoint = endpoint
        self.id_arg = id_arg
        self.url_args = url_args

    def get_url(self, row_id, row):
        kwargs = dict(self.url_args) if self.url_args else {}
        kwargs[self.id_arg] = row_id
        url = url_for(self.endpoint, **kwargs)
        return url


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
