from ..emailer.base import Emailer
from ..extension_core.base import Extension


class EmailerExtension(Extension):
    @property
    def name(self) -> str:
        return "emailer"

    def init_app(self, app):
        self._emailer = Emailer()
        self._emailer.init_app(app)

    def get_emailer(self):
        return self._emailer
