from ..admin import Admin, AdminViewMixin
from ..extension_core.base import Extension


class AdminExtension(Extension):
    @property
    def name(self) -> str:
        return "admin"

    def init_app(self, app):
        self._admin = Admin()
        self._admin.init_app(app)

    def get_admin(self):
        return self._admin

    def post_init(self, app):
        """Collect views from every extension that implements AdminViewMixin.

        Runs after all extensions' init_app, so this does not care whether
        admin was registered before or after its view providers.

        Note: this only sees extensions registered up to this point. An
        extension registered via ExtensionManager.register_extension *after*
        app.init_app() has already run will not be rescanned automatically
        (same limitation the previous push-based implementation had).
        """
        exts = app.extensions["exts"]
        for ext in exts.list_extensions():
            if isinstance(ext, AdminViewMixin):
                for view, is_menu in ext.get_admin_views():
                    self._admin.register_view(view, is_menu=is_menu)
