from flask import url_for
from flask_babel import gettext


class BaseListRowAction:
    def __init__(self, type=None, title=None, icon=None):
        self.type = type
        self.title = title
        self.icon = icon


class LinkRowAction(BaseListRowAction):
    def __init__(self, url, title=None, icon=None):
        super().__init__(type="link", title=title, icon=icon)
        self.url = url

    def get_url(self, row_id, row):
        if isinstance(self.url, str):
            url = self.url.format(row_id=row_id)
        else:
            url = self.url(self, row_id, row)
        return url


class EndpointLinkRowAction(BaseListRowAction):
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


class ViewRowAction(BaseListRowAction):
    def __init__(self):
        super().__init__(type="view_row", title=gettext("View Record"), icon="eye")


class ViewPopupRowAction(BaseListRowAction):
    def __init__(self):
        super().__init__(
            type="view_row_popup", title=gettext("View Record"), icon="eye"
        )


class EditRowAction(BaseListRowAction):
    def __init__(self):
        super().__init__(type="edit_row", title=gettext("Edit Record"), icon="pencil")


class EditPopupRowAction(BaseListRowAction):
    def __init__(self):
        super().__init__(
            type="edit_row_popup", title=gettext("Edit Record"), icon="pencil"
        )


class DeleteRowAction(BaseListRowAction):
    def __init__(self):
        super().__init__(
            type="delete_row", title=gettext("Delete Record"), icon="trash"
        )
