from ..datastore.sqla import db
from ..extension_core.base import Extension


class DatabaseExtension(Extension):
    @property
    def name(self) -> str:
        return "database"

    def init_app(self, app):
        db.init_app(app)

    def shutdown(self):
        db.dispose()
