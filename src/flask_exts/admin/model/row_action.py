from flask import url_for
from flask_babel import gettext


class BaseRowAction:
    def __init__(self, type=None, title=None, icon=None):
        self.type = type
        self.title = title
        self.icon = icon


class ViewRowAction(BaseRowAction):
    def __init__(self):
        super().__init__(type="view_row", title=gettext("View Record"), icon="eye")


class ViewPopupRowAction(BaseRowAction):
    def __init__(self):
        super().__init__(
            type="view_row_popup", title=gettext("View Record"), icon="eye"
        )


class EditRowAction(BaseRowAction):
    def __init__(self):
        super().__init__(type="edit_row", title=gettext("Edit Record"), icon="pencil")


class EditPopupRowAction(BaseRowAction):
    def __init__(self):
        super().__init__(
            type="edit_row_popup", title=gettext("Edit Record"), icon="pencil"
        )


class DeleteRowAction(BaseRowAction):
    def __init__(self):
        super().__init__(
            type="delete_row", title=gettext("Delete Record"), icon="trash"
        )
        self.confirm = gettext('Are you sure you want to delete this record?')


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
