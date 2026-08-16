from ..extension import Extension


class DatabaseExtension(Extension):
    @property
    def name(self) -> str:
        return "database"

    @property
    def priority(self) -> int:
        return 10

    def init_app(self, app):
        from ..datastore.sqla import db

        db.init_app(app)
