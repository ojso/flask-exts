from ..extension import Extension


class EmailExtension(Extension):
    @property
    def name(self) -> str:
        return "email"

    @property
    def priority(self) -> int:
        return 10

    def init_app(self, app):
        from ..email.base import Email

        self._email = Email()
        self._email.init_app(app)
