from ..extension import Extension


class StartupExtension(Extension):
    @property
    def name(self) -> str:
        return "startup"

    @property
    def priority(self) -> int:
        return 50

    def init_app(self, app):
        from ..startup import setting

        setting(app)
