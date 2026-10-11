from ..extension_core.base import Extension
from ..portal.index_view import IndexView


class PortalExtension(Extension):
    @property
    def name(self) -> str:
        return "portal"

    def init_app(self, app):
        pass

    def get_admin_views(self):
        return [(IndexView(), False)]
