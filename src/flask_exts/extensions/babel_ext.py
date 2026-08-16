from ..extension import Extension


class BabelExtension(Extension):
    @property
    def name(self) -> str:
        return "babel"

    @property
    def priority(self) -> int:
        return 10

    def init_app(self, app):
        from ..babel import babel_init_app

        babel_init_app(app)
