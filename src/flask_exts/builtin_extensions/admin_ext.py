from ..admin import Admin, AdminViewMixin
from ..extension_core.base import Extension


class AdminExtension(Extension):
    @property
    def name(self) -> str:
        return "admin"

    def __init__(self):
        self._admin = None
        self._registered_view_names = set()

    def init_app(self, app):
        self._admin = Admin()
        self._admin.init_app(app)

    def get_admin(self):
        return self._admin

    def post_init(self, app):
        """Collect views from every extension that implements AdminViewMixin."""
        self.rescan_views(app)

    def on_extension_registered(self, app, extension):
        """Pick up views from a provider registered after app initialization."""
        if isinstance(extension, AdminViewMixin):
            self.rescan_views(app)

    def rescan_views(self, app):
        """Register views published by ``AdminViewMixin`` providers.

        Safe to call more than once: views whose names are already registered
        are skipped, so late registrations and explicit rescans do not raise
        duplicate-view errors.
        """
        exts = app.extensions["exts"]
        for ext in exts.list_extensions():
            if not isinstance(ext, AdminViewMixin):
                continue
            for view, is_menu in ext.get_admin_views():
                view_name = view.name.lower().replace(" ", "")
                if view_name in self._registered_view_names:
                    continue
                self._admin.register_view(view, is_menu=is_menu)
                self._registered_view_names.add(view_name)
