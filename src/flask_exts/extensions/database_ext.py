from ..extension_core.base import Extension
from ..datastore.sqla import db


class DatabaseExtension(Extension):
    @property
    def name(self) -> str:
        return "database"

    @property
    def priority(self) -> int:
        return 10

    def init_app(self, app):
        db.init_app(app)
